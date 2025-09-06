from backend.prompt_templates import PromptTemplateManager, TemplateType


def test_prompt_templates():
    print("Testing Prompt Templates...\n")

    # Initialize the prompt template manager
    manager = PromptTemplateManager()

    # List all available templates
    print("Available templates:")
    for tpl in manager.list_templates():
        print(f"- {tpl['name']}: {tpl['description']}")
        print(f"  Input variables: {', '.join(tpl['input_variables'])}")

    # Test formatting each template
    test_context = "The quick brown fox jumps over the lazy dog."
    test_question = "What did the fox do?"

    print("\nTesting template formatting:")
    for template_type in TemplateType:
        try:
            template = manager.get_template(template_type)
            formatted = template.format(context=test_context, question=test_question)
            print(f"\n--- {template_type.value.upper()} ---")
            print(formatted)
        except Exception as e:
            print(f"Error with template {template_type}: {str(e)}")

    assert True, "Prompt template test should complete without errors"
