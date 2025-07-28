#!/usr/bin/env python3
"""
Batch processing functionality for medical literature annotation
"""

import os
import json
import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from .core import MedicalAnnotationLLM, AnnotationResult
from ..common import BaseProcessor, ProcessingResult, timer, ensure_directory
from ..common.exceptions import AnnotationError, FileError


class BatchProcessor(BaseProcessor):
    """Batch processor for medical literature annotation"""

    def __init__(self,
                 api_key: str,
                 model: str = "deepseek-chat",
                 model_type: str = "deepseek",
                 base_url: Optional[str] = None,
                 max_retries: int = 3,
                 retry_delay: int = 5,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize batch processor

        Args:
            api_key: API key for LLM service
            model: Model name to use
            model_type: Type of model service
            base_url: Base URL for API (optional)
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            config: Additional configuration
        """
        super().__init__(config)

        # Initialize annotator
        self.annotator = MedicalAnnotationLLM(
            api_key=api_key,
            model=model,
            model_type=model_type,
            base_url=base_url,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def process(self, input_data: Any) -> ProcessingResult:
        """
        Process input data (not used for batch processing)

        Args:
            input_data: Input data

        Returns:
            ProcessingResult: Processing result
        """
        return ProcessingResult(
            success=False,
            message="Use process_directory method for batch processing",
            data=None
        )

    @timer
    def process_directory(self,
                         data_dir: str,
                         output_dir: Optional[str] = None,
                         skip_existing: bool = True) -> ProcessingResult:
        """
        Process all Excel files in a directory

        Args:
            data_dir: Directory containing Excel files
            output_dir: Output directory (deprecated, saves in annotation subdirs)
            skip_existing: Skip already processed files

        Returns:
            ProcessingResult: Processing result
        """
        try:
            # Find all Excel files
            excel_files = []
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.endswith('.xlsx'):
                        excel_files.append(os.path.join(root, file))

            self.logger.info(f"Found {len(excel_files)} Excel files to process")

            processed_count = 0
            skipped_count = 0
            failed_count = 0
            failed_files = []

            for file_path in excel_files:
                try:
                    self.logger.info(f"Processing {file_path}")

                    # Create annotation directory
                    dir_path = os.path.dirname(file_path)
                    annotation_dir = os.path.join(dir_path, "annotation")
                    ensure_directory(annotation_dir)

                    # Generate output file name
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    output_file = os.path.join(
                        annotation_dir,
                        f"{base_name}_annotated_{self.annotator.model_type}.json"
                    )
                    stats_file = os.path.join(
                        annotation_dir,
                        f"{base_name}_stats_{self.annotator.model_type}.json"
                    )

                    # Check if already processed
                    if skip_existing and os.path.exists(output_file):
                        self.logger.info(f"Skipping already processed file: {output_file}")
                        skipped_count += 1
                        continue

                    # Process file with retries
                    success = False
                    for attempt in range(self.max_retries):
                        try:
                            # Process file
                            results = self.annotator.annotate_excel_file(file_path)

                            if results:
                                # Save results
                                self.annotator.save_results(results, output_file)

                                # Generate and save statistics
                                stats = self.annotator.generate_statistics(results)
                                with open(stats_file, 'w', encoding='utf-8') as f:
                                    json.dump(stats, f, ensure_ascii=False, indent=2)

                                self.logger.info(f"Results saved to {output_file}")
                                processed_count += 1
                                success = True
                                break
                            else:
                                self.logger.warning(f"No results for {file_path}")

                        except Exception as e:
                            self.logger.warning(f"Attempt {attempt + 1} failed for {file_path}: {e}")
                            if attempt < self.max_retries - 1:
                                time.sleep(self.retry_delay)
                            else:
                                failed_files.append(file_path)
                                failed_count += 1
                                break

                    if not success and file_path not in failed_files:
                        failed_files.append(file_path)
                        failed_count += 1

                except Exception as e:
                    self.logger.error(f"Error processing {file_path}: {e}")
                    failed_files.append(file_path)
                    failed_count += 1
                    continue

            # Summary
            summary = {
                "total_files": len(excel_files),
                "processed": processed_count,
                "skipped": skipped_count,
                "failed": failed_count,
                "failed_files": failed_files
            }

            self.logger.info(f"Batch processing completed: {summary}")

            return ProcessingResult(
                success=True,
                message=f"Processed {processed_count}/{len(excel_files)} files successfully",
                data=summary
            )

        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return ProcessingResult(
                success=False,
                message=f"Batch processing failed: {e}",
                error=e
            )

    def get_processing_status(self, data_dir: str) -> Dict[str, Any]:
        """
        Get processing status for a directory

        Args:
            data_dir: Data directory

        Returns:
            Dict[str, Any]: Processing status
        """
        total_files = 0
        processed_files = 0

        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.xlsx'):
                    total_files += 1

                    # Check if processed
                    base_name = os.path.splitext(file)[0]
                    annotation_dir = os.path.join(root, 'annotation')
                    result_file = os.path.join(
                        annotation_dir,
                        f"{base_name}_annotated_{self.annotator.model_type}.json"
                    )

                    if os.path.exists(result_file):
                        processed_files += 1

        return {
            "total_files": total_files,
            "processed_files": processed_files,
            "remaining_files": total_files - processed_files,
            "completion_percentage": (processed_files / total_files * 100) if total_files > 0 else 0
        }


def batch_process_directory(data_dir: str,
                           output_dir: Optional[str] = None,
                           api_key: Optional[str] = None,
                           model: str = "deepseek-chat",
                           model_type: str = "deepseek",
                           base_url: Optional[str] = None,
                           max_retries: int = 3,
                           retry_delay: int = 5) -> ProcessingResult:
    """
    Batch process directory (convenience function)

    Args:
        data_dir: Directory containing Excel files
        output_dir: Output directory (deprecated)
        api_key: API key for LLM service
        model: Model name to use
        model_type: Type of model service
        base_url: Base URL for API (optional)
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds

    Returns:
        ProcessingResult: Processing result
    """
    if api_key is None:
        raise AnnotationError("API key is required")

    # Create processor
    processor = BatchProcessor(
        api_key=api_key,
        model=model,
        model_type=model_type,
        base_url=base_url,
        max_retries=max_retries,
        retry_delay=retry_delay
    )

    # Process directory
    return processor.process_directory(data_dir)


class DistributedBatchProcessor(BatchProcessor):
    """Distributed batch processor for large-scale processing"""

    def __init__(self, *args, **kwargs):
        """Initialize distributed processor"""
        super().__init__(*args, **kwargs)
        self.workers = kwargs.get('workers', 1)
        self.chunk_size = kwargs.get('chunk_size', 10)

    def process_directory(self,
                         data_dir: str,
                         output_dir: Optional[str] = None,
                         skip_existing: bool = True) -> ProcessingResult:
        """
        Process directory with multiple workers (placeholder for future implementation)

        Args:
            data_dir: Directory containing Excel files
            output_dir: Output directory (deprecated)
            skip_existing: Skip already processed files

        Returns:
            ProcessingResult: Processing result
        """
        # For now, fall back to single-threaded processing
        # TODO: Implement multiprocessing/threading
        self.logger.info(f"Using {self.workers} workers (not implemented yet, using single thread)")
        return super().process_directory(data_dir, output_dir, skip_existing)


class ResumableBatchProcessor(BatchProcessor):
    """Batch processor with resume capability"""

    def __init__(self, *args, **kwargs):
        """Initialize resumable processor"""
        super().__init__(*args, **kwargs)
        self.checkpoint_file = kwargs.get('checkpoint_file', 'processing_checkpoint.json')

    def save_checkpoint(self, processed_files: List[str], failed_files: List[str]) -> None:
        """
        Save processing checkpoint

        Args:
            processed_files: List of processed files
            failed_files: List of failed files
        """
        checkpoint_data = {
            "processed_files": processed_files,
            "failed_files": failed_files,
            "timestamp": time.time()
        }

        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

    def load_checkpoint(self) -> Dict[str, Any]:
        """
        Load processing checkpoint

        Returns:
            Dict[str, Any]: Checkpoint data
        """
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load checkpoint: {e}")

        return {"processed_files": [], "failed_files": [], "timestamp": 0}

    def process_directory(self,
                         data_dir: str,
                         output_dir: Optional[str] = None,
                         skip_existing: bool = True) -> ProcessingResult:
        """
        Process directory with resume capability

        Args:
            data_dir: Directory containing Excel files
            output_dir: Output directory (deprecated)
            skip_existing: Skip already processed files

        Returns:
            ProcessingResult: Processing result
        """
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        processed_files = set(checkpoint.get("processed_files", []))

        self.logger.info(f"Resuming from checkpoint with {len(processed_files)} processed files")

        # Process directory
        result = super().process_directory(data_dir, output_dir, skip_existing)

        # Update checkpoint if successful
        if result.success and result.data:
            # Save updated checkpoint
            all_processed = list(processed_files)
            if 'processed_files' in result.data:
                all_processed.extend(result.data['processed_files'])

            self.save_checkpoint(
                all_processed,
                result.data.get('failed_files', [])
            )

        return result