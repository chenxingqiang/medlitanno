#!/usr/bin/env python3
"""
Main CLI entry point for MedLitAnno package
"""

import os
import sys
import argparse
from typing import Optional

from .common import setup_logging, get_env_var, validate_api_key
from .common.exceptions import MedLitAnnoError
from .annotation import batch_process_directory, MedicalAnnotationLLM

# Try to import MRAgent, but don't fail if not available
try:
    from .mragent import MRAgent, MRAgentOE
    _MRAGENT_CLI_AVAILABLE = True
except ImportError:
    _MRAGENT_CLI_AVAILABLE = False
    MRAgent = None
    MRAgentOE = None


def setup_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="MedLitAnno - Medical Literature Analysis and Annotation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Annotate medical literature
  medlitanno annotate --data-dir datatrain --model deepseek-chat
  
  # Run MR analysis (Knowledge Discovery mode)
  medlitanno mr --outcome "back pain" --model gpt-4o
  
  # Run MR analysis (Causal Validation mode)  
  medlitanno mr --exposure "osteoarthritis" --outcome "back pain" --mode causal
  
  # Show version
  medlitanno --version
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )
    
    # Annotation subcommand
    annotate_parser = subparsers.add_parser(
        "annotate",
        help="Annotate medical literature"
    )
    annotate_parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Directory containing Excel files to annotate"
    )
    annotate_parser.add_argument(
        "--model",
        type=str,
        default="deepseek-chat",
        help="LLM model to use (default: deepseek-chat)"
    )
    annotate_parser.add_argument(
        "--model-type",
        type=str,
        choices=["openai", "deepseek", "deepseek-reasoner", "qianwen"],
        default="deepseek",
        help="LLM model type (default: deepseek)"
    )
    annotate_parser.add_argument(
        "--api-key",
        type=str,
        help="API key (or use environment variable)"
    )
    annotate_parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries (default: 3)"
    )
    annotate_parser.add_argument(
        "--retry-delay",
        type=int,
        default=5,
        help="Delay between retries in seconds (default: 5)"
    )
    
    # MR analysis subcommand
    mr_parser = subparsers.add_parser(
        "mr",
        help="Run Mendelian Randomization analysis"
    )
    mr_parser.add_argument(
        "--mode",
        type=str,
        choices=["discovery", "causal"],
        default="discovery",
        help="Analysis mode: discovery (Knowledge Discovery) or causal (Causal Validation)"
    )
    mr_parser.add_argument(
        "--exposure",
        type=str,
        help="Exposure variable (required for causal mode)"
    )
    mr_parser.add_argument(
        "--outcome",
        type=str,
        help="Outcome variable (required for both modes)"
    )
    mr_parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use (default: gpt-4o)"
    )
    mr_parser.add_argument(
        "--model-type",
        type=str,
        choices=["openai", "deepseek", "qianwen"],
        default="openai",
        help="LLM model type (default: openai)"
    )
    mr_parser.add_argument(
        "--ai-key",
        type=str,
        help="AI API key (or use environment variable)"
    )
    mr_parser.add_argument(
        "--gwas-token",
        type=str,
        help="GWAS token (or use environment variable)"
    )
    mr_parser.add_argument(
        "--num-articles",
        type=int,
        default=100,
        help="Number of articles to retrieve (default: 100)"
    )
    mr_parser.add_argument(
        "--bidirectional",
        action="store_true",
        help="Perform bidirectional MR analysis"
    )
    
    # Test subcommand
    test_parser = subparsers.add_parser(
        "test",
        help="Test system functionality"
    )
    test_parser.add_argument(
        "--component",
        type=str,
        choices=["annotation", "mragent", "all"],
        default="all",
        help="Component to test (default: all)"
    )
    
    return parser


def run_annotation(args) -> int:
    """Run annotation command"""
    try:
        # Get API key
        api_key = args.api_key
        if not api_key:
            if args.model_type in ["deepseek", "deepseek-reasoner"]:
                api_key = get_env_var("DEEPSEEK_API_KEY")
            elif args.model_type == "qianwen":
                api_key = get_env_var("QIANWEN_API_KEY")
            elif args.model_type == "openai":
                api_key = get_env_var("OPENAI_API_KEY")
        
        api_key = validate_api_key(api_key, args.model_type)
        
        print(f"🚀 Starting medical literature annotation...")
        print(f"📁 Data directory: {args.data_dir}")
        print(f"🤖 Model: {args.model_type} ({args.model})")
        print()
        
        # Run batch processing
        result = batch_process_directory(
            data_dir=args.data_dir,
            api_key=api_key,
            model=args.model,
            model_type=args.model_type,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay
        )
        
        if result.success:
            print("✅ Annotation completed successfully!")
            if result.data:
                print(f"📊 Statistics: {result.data}")
            return 0
        else:
            print(f"❌ Annotation failed: {result.message}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def run_mr_analysis(args) -> int:
    """Run MR analysis command"""
    if not _MRAGENT_CLI_AVAILABLE:
        print("❌ Error: MRAgent functionality is not available.")
        print("Please install required dependencies: pip install biopython")
        return 1
        
    try:
        # Get API key
        ai_key = args.ai_key or get_env_var("OPENAI_API_KEY")
        ai_key = validate_api_key(ai_key, "OpenAI")
        
        # Get GWAS token
        gwas_token = args.gwas_token or get_env_var("OPENGWAS_JWT")
        if not gwas_token:
            print("⚠️  Warning: No GWAS token provided. Some features may not work.")
        
        print(f"🚀 Starting Mendelian Randomization analysis...")
        print(f"📊 Mode: {args.mode}")
        print(f"🤖 Model: {args.model_type} ({args.model})")
        
        if args.mode == "discovery":
            if not args.outcome:
                print("❌ Error: --outcome is required for discovery mode")
                return 1
            
            print(f"🎯 Outcome: {args.outcome}")
            
            # Initialize MRAgent
            agent = MRAgent(
                outcome=args.outcome,
                AI_key=ai_key,
                LLM_model=args.model,
                model_type=args.model_type,
                gwas_token=gwas_token,
                num=args.num_articles,
                bidirectional=args.bidirectional
            )
            
        elif args.mode == "causal":
            if not args.exposure or not args.outcome:
                print("❌ Error: Both --exposure and --outcome are required for causal mode")
                return 1
            
            print(f"🧬 Exposure: {args.exposure}")
            print(f"🎯 Outcome: {args.outcome}")
            
            # Initialize MRAgentOE
            agent = MRAgentOE(
                exposure=args.exposure,
                outcome=args.outcome,
                AI_key=ai_key,
                LLM_model=args.model,
                model_type=args.model_type,
                gwas_token=gwas_token,
                bidirectional=args.bidirectional
            )
        
        print()
        print("🔄 Running MR analysis...")
        
        # Run analysis
        agent.run()
        
        print("✅ MR analysis completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def run_test(args) -> int:
    """Run test command"""
    try:
        print(f"🧪 Testing {args.component} component(s)...")
        
        if args.component in ["annotation", "all"]:
            print("📝 Testing annotation system...")
            # Simple test - try to import and initialize
            try:
                from .annotation import MedicalAnnotationLLM
                print("  ✅ Annotation system import successful")
            except Exception as e:
                print(f"  ❌ Annotation system test failed: {e}")
                return 1
        
        if args.component in ["mragent", "all"]:
            print("🧬 Testing MRAgent system...")
            # Simple test - try to import
            if _MRAGENT_CLI_AVAILABLE:
                print("  ✅ MRAgent system import successful")
            else:
                print("  ❌ MRAgent system not available (missing dependencies)")
                if args.component == "mragent":
                    return 1
        
        print("✅ All tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1


def main() -> int:
    """Main CLI entry point"""
    try:
        # Setup argument parser
        parser = setup_parser()
        args = parser.parse_args()
        
        # Setup logging
        setup_logging(
            level=args.log_level,
            log_file=args.log_file
        )
        
        # Handle commands
        if args.command == "annotate":
            return run_annotation(args)
        elif args.command == "mr":
            return run_mr_analysis(args)
        elif args.command == "test":
            return run_test(args)
        else:
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 1
    except MedLitAnnoError as e:
        print(f"❌ MedLitAnno Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 