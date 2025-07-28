#!/usr/bin/env python3
"""
MedLitAnno Package Demo

This script demonstrates the new unified package structure and capabilities.
"""

import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def demo_annotation_system():
    """Demonstrate the annotation system"""
    print("🔬 Medical Literature Annotation System Demo")
    print("=" * 50)
    
    try:
        from medlitanno import MedicalAnnotationLLM, Entity, Evidence, Relation, AnnotationResult
        print("✅ Successfully imported annotation classes")
        
        # Create a demo annotator (without real API key)
        print("\n📝 Creating annotation system...")
        annotator = MedicalAnnotationLLM(
            api_key="demo_key",
            model="deepseek-chat",
            model_type="deepseek"
        )
        print(f"✅ Annotator initialized: {annotator.model_type} - {annotator.model}")
        
        # Demo data structures
        print("\n📊 Demo data structures:")
        
        # Create sample entity
        entity = Entity(
            text="Helicobacter pylori",
            label="Bacteria",
            start_pos=10,
            end_pos=28
        )
        print(f"Entity: {entity}")
        
        # Create sample evidence
        evidence = Evidence(
            text="H. pylori infection triggers autoimmune responses",
            start_pos=30,
            end_pos=80,
            relation_type="contributes_to"
        )
        print(f"Evidence: {evidence}")
        
        # Create sample relation
        disease_entity = Entity(
            text="autoimmune gastritis",
            label="Disease", 
            start_pos=85,
            end_pos=105
        )
        
        relation = Relation(
            subject=entity,
            object=disease_entity,
            evidence=evidence,
            relation_type="contributes_to"
        )
        print(f"Relation: {relation}")
        
        # Create annotation result
        result = AnnotationResult(
            pmid="12345678",
            title="H. pylori and autoimmune diseases",
            abstract="Background: H. pylori infection has been associated with autoimmune diseases...",
            entities=[entity, disease_entity],
            evidences=[evidence],
            relations=[relation]
        )
        
        print(f"\n📋 Annotation Result:")
        stats = result.get_statistics()
        print(f"  - Total entities: {stats['total_entities']}")
        print(f"  - Bacteria entities: {stats['bacteria_entities']}")
        print(f"  - Disease entities: {stats['disease_entities']}")
        print(f"  - Total relations: {stats['total_relations']}")
        print(f"  - Relation types: {stats['relation_types']}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_common_utilities():
    """Demonstrate common utilities"""
    print("\n🛠️ Common Utilities Demo")
    print("=" * 50)
    
    try:
        from medlitanno.common import LLMClient, LLMConfig, timer, setup_logging
        print("✅ Successfully imported common utilities")
        
        # Demo LLM configuration
        print("\n🤖 LLM Configuration:")
        config = LLMConfig(
            api_key="demo_key",
            model="deepseek-chat",
            model_type="deepseek",
            max_retries=3,
            temperature=0.1
        )
        print(f"  - Model: {config.model}")
        print(f"  - Type: {config.model_type}")
        print(f"  - Max retries: {config.max_retries}")
        print(f"  - Temperature: {config.temperature}")
        
        # Demo timer decorator
        print("\n⏱️ Timer Decorator Demo:")
        
        @timer
        def demo_function():
            import time
            time.sleep(0.1)
            return "Demo completed"
        
        result = demo_function()
        print(f"Function result: {result}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_batch_processing():
    """Demonstrate batch processing capabilities"""
    print("\n🔄 Batch Processing Demo")
    print("=" * 50)
    
    try:
        from medlitanno.annotation import BatchProcessor
        print("✅ Successfully imported batch processor")
        
        # Demo processor configuration
        print("\n⚙️ Processor Configuration:")
        processor = BatchProcessor(
            api_key="demo_key",
            model="deepseek-reasoner",
            model_type="deepseek-reasoner",
            max_retries=5,
            retry_delay=10
        )
        print(f"  - Model: {processor.annotator.model}")
        print(f"  - Type: {processor.annotator.model_type}")
        print(f"  - Max retries: {processor.max_retries}")
        print(f"  - Retry delay: {processor.retry_delay}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_format_conversion():
    """Demonstrate format conversion"""
    print("\n🔄 Format Conversion Demo")
    print("=" * 50)
    
    try:
        from medlitanno.annotation import LabelStudioConverter, CSVConverter
        print("✅ Successfully imported format converters")
        
        # Demo converters
        print("\n📊 Available Converters:")
        
        ls_converter = LabelStudioConverter()
        print("  - Label Studio Converter: ✅")
        
        csv_converter = CSVConverter()
        print("  - CSV Converter: ✅")
        
        # Demo Label Studio config
        config = ls_converter.create_label_config()
        print(f"\n🏷️ Label Studio Config Created:")
        print(f"  - Type: {config['type']}")
        print(f"  - Children: {len(config['children'])} components")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_mragent_system():
    """Demonstrate MRAgent system (if available)"""
    print("\n🧬 MRAgent System Demo")
    print("=" * 50)
    
    try:
        from medlitanno import MRAgent, MRAgentOE
        print("✅ Successfully imported MRAgent classes")
        
        # Demo agent info
        print("\n📊 MRAgent Capabilities:")
        print("  - Knowledge Discovery Mode: ✅")
        print("  - Causal Validation Mode: ✅")
        print("  - GWAS Integration: ✅")
        print("  - Literature Analysis: ✅")
        
    except ImportError as e:
        print(f"⚠️  MRAgent not available: {e}")
        print("  💡 To enable MRAgent: pip install biopython")


def main():
    """Main demo function"""
    print("🚀 MedLitAnno Package Demo")
    print("=" * 60)
    print("Demonstrating the unified medical literature analysis package")
    print()
    
    # Run demos
    demo_annotation_system()
    demo_common_utilities()
    demo_batch_processing()
    demo_format_conversion()
    demo_mragent_system()
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\n📚 Next Steps:")
    print("  1. Set up your API keys (DEEPSEEK_API_KEY, QIANWEN_API_KEY)")
    print("  2. Prepare your Excel data files")
    print("  3. Run: python -m medlitanno annotate --data-dir your_data")
    print("  4. Monitor progress: python -m medlitanno test")
    print("\n📖 Documentation: https://github.com/chenxingqiang/medlitanno")


if __name__ == "__main__":
    main() 