from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from enum import Enum

class TemplateType(str, Enum):
    """Types of prompt templates"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    STEP_BY_STEP = "step_by_step"
    CONTEXT_FIRST = "context_first"
    QUESTION_FIRST = "question_first"

class PromptTemplate(BaseModel):
    """A prompt template for RAG systems"""
    name: str
    description: str
    template: str
    input_variables: List[str]
    
    def format(self, **kwargs) -> str:
        """Format the template with the given variables"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required template variable: {e}")

class PromptTemplateManager:
    """Manages prompt templates for the RAG system"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, PromptTemplate]:
        """Load default prompt templates"""
        return {
            TemplateType.SIMPLE: PromptTemplate(
                name="simple",
                description="A simple prompt template for general question answering",
                template="""Answer the following question based on the provided context.

Context: {context}

Question: {question}

Answer:""",
                input_variables=["context", "question"]
            ),
            TemplateType.DETAILED: PromptTemplate(
                name="detailed",
                description="A detailed prompt template that asks for explanations",
                template="""Please provide a detailed answer to the question based on the given context. 
Include relevant details and explanations in your response.

Context: {context}

Question: {question}

Please provide a detailed answer:""",
                input_variables=["context", "question"]
            ),
            TemplateType.STEP_BY_STEP: PromptTemplate(
                name="step_by_step",
                description="A template that asks for step-by-step reasoning",
                template="""Please answer the following question step by step based on the provided context.

Context: {context}

Question: {question}

Let's think step by step:""",
                input_variables=["context", "question"]
            ),
            TemplateType.CONTEXT_FIRST: PromptTemplate(
                name="context_first",
                description="A template that emphasizes the context first",
                template="""Here is some context that might be relevant to answer the question:

{context}

Based on the above context, answer the following question: {question}

Answer:""",
                input_variables=["context", "question"]
            ),
            TemplateType.QUESTION_FIRST: PromptTemplate(
                name="question_first",
                description="A template that puts the question first",
                template="""Question: {question}

Here is some context that might help answer the question:

{context}

Based on the above context, the answer is:""",
                input_variables=["question", "context"]
            )
        }
    
    def get_template(self, template_type: TemplateType) -> PromptTemplate:
        """Get a template by type"""
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        return self.templates[template_type]
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template"""
        if template.name in self.templates:
            raise ValueError(f"Template with name '{template.name}' already exists")
        self.templates[template.name] = template
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return [
            {
                "name": tpl.name,
                "description": tpl.description,
                "input_variables": tpl.input_variables
            }
            for tpl in self.templates.values()
        ]
    
    def format_prompt(
        self, 
        template_type: TemplateType, 
        **kwargs
    ) -> str:
        """Format a prompt using the specified template"""
        template = self.get_template(template_type)
        return template.format(**kwargs)

# Global instance for easy access
prompt_manager = PromptTemplateManager()

def get_prompt_manager() -> PromptTemplateManager:
    """Get the global prompt template manager"""
    return prompt_manager
