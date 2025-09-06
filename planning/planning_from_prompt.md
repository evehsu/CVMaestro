# CVMaestro Backend Implementation Plan

## Overview
Python-only backend implementation with terminal-based user interaction. Focus on core resume processing logic and AI-powered content refinement.

## Phase 1: Core Domain Architecture & Class Definitions (Weeks 1-2)

### 1.1 Core Domain Classes

#### Resume Class
```python
class Resume:
    # Attributes
    raw_content: Dict[str, str]      # {section_name: content_text}
    revised_content: Dict[str, str]  # {section_name: improved_content}
    template: str                    # template identifier/type, optional for now
    
    # Methods
    def load_resume(self, file_path:str) -> str:
         """load user resume file """
         pass

    def parse_resume(self, content: str) -> None:
        """Parse user resume file and populate raw_content by sections"""
        pass
    
    def get_section(self, section_name: str) -> str:
        """Get content for specific resume section"""
        pass
    
    def update_section(self, section_name: str, content: str) -> None:
        """Update content for specific section"""
        pass
    
    def export_markdown(self) -> str:
        """Generate final markdown resume"""
        pass
```

#### UserProfile Class
```python
class UserProfile:
    # Attributes
    years_of_experience: int
    target_level: str  # junior, mid, senior, executive
    target_position: str
    
    # Methods
    def validate_profile(self) -> bool:
        """Validate profile completeness and consistency"""
        pass
    
    def get_experience_tier(self) -> str:
        """Categorize experience level for template selection"""
        pass
```

#### JobDescription Class
```python
class JobDescription:
    # Attributes
    job_level: str
    job_responsibility_summary: str
    job_skill_requirements: List[str]
    raw_jd_text: str
    
    # Methods  
    def parse_job_description(self, jd_text: str) -> None:
        """Parse job description and extract key attributes"""
        pass
    
    def extract_keywords(self) -> List[str]:
        """Extract important keywords for ATS optimization"""
        pass
    
    def get_skill_priorities(self) -> Dict[str, int]:
        """Rank skills by importance/frequency"""
        pass
```

#### ResumeProblem Class
```python
class ResumeProblem:
    # Attributes
    overall_quality_score: float
    section_problems: Dict[str, List[str]]  # {section: [problem_list]}
    missing_sections: List[str]
    improvement_suggestions: Dict[str, List[str]]
    
    # Methods
    def add_problem(self, section: str, problem: str) -> None:
        """Add identified problem for a section"""
        pass
    
    def mark_resolved(self, section: str, problem: str) -> None:
        """Mark a problem as resolved"""
        pass
    
    def get_priority_issues(self) -> List[Tuple[str, str]]:
        """Get high-priority issues to address first"""
        pass
```

### 1.2 Service Layer Interfaces

#### ContentAnalysisService
```python
class ContentAnalysisService:
    def analyze_resume_quality(self, resume: Resume) -> ResumeProblem:
        """Analyze resume and identify quality issues"""
        pass
    
    def suggest_improvements(self, section_content: str, section_type: str) -> List[str]:
        """Generate improvement suggestions for section"""
        pass
```

#### TemplateService
```python
class TemplateService:
    def recommend_template(self, user_profile: UserProfile) -> str:
        """Recommend appropriate template based on profile"""
        pass
    
    def get_section_order(self, template: str) -> List[str]:
        """Get recommended section order for template"""
        pass
```

#### JobOptimizationService
```python
class JobOptimizationService:
    def optimize_content(self, resume: Resume, job_desc: JobDescription) -> Dict[str, str]:
        """Optimize resume content for specific job description"""
        pass
    
    def calculate_match_score(self, resume: Resume, job_desc: JobDescription) -> float:
        """Calculate how well resume matches job requirements"""
        pass
```

## Phase 2: MVP Backend Implementation (Weeks 3-4)

### 2.1 Core Implementation Priorities
1. **Resume parsing** (markdown files only)
2. **Basic content analysis** with simple quality scoring
3. **Gap identification** and user prompt system  
4. **Content improvement** using LLM integration
5. **Terminal-based interaction** for user input collection

### 2.2 MVP Feature Set
- Parse uploaded resume markdown file
- Identify missing/weak sections
- Interactive terminal prompts for additional information
- Generate improved resume sections
- Export final markdown resume

### 2.3 Terminal Interface Design
```python
class TerminalInterface:
    def collect_user_profile(self) -> UserProfile:
        """Interactive prompt to collect user profile information"""
        pass
    
    def prompt_for_missing_info(self, section: str, questions: List[str]) -> Dict[str, str]:
        """Prompt user for specific missing information"""
        pass
    
    def display_problems(self, problems: ResumeProblem) -> None:
        """Show identified issues to user"""
        pass
    
    def confirm_changes(self, section: str, old_content: str, new_content: str) -> bool:
        """Show proposed changes and get user confirmation"""
        pass
```

## Phase 3: Enhanced Content Processing (Weeks 5-6)

### 3.1 Advanced Content Analysis
- Implement sophisticated resume parsing for different formats
- Add industry-specific content evaluation
- Build comprehensive gap detection algorithms

### 3.2 AI Integration Enhancement
- Integrate with LLM APIs for content improvement
- Implement context-aware content suggestions
- Add professional language enhancement

### 3.3 Template Intelligence
- Build template recommendation system
- Implement section reordering based on profile
- Add template-specific content optimization

## Phase 4: Job Description Optimization (Weeks 7-8)

### 4.1 JD Analysis Implementation
- Complete JobDescription parsing methods
- Build keyword extraction and ranking
- Implement ATS optimization scoring

### 4.2 Content Optimization Engine
- Dynamic content adjustment based on JD requirements
- Keyword integration without over-stuffing
- Section prioritization for job relevance

### 4.3 Iterative Refinement System
- Implement the full 3-step workflow from PRD
- Build conversation state management
- Add sophisticated problem resolution logic

## Phase 5: Multi-Format & Advanced Features (Weeks 9-10)

### 5.1 File Format Support
- Add PDF parsing capabilities
- Implement Word document processing
- Build cross-format consistency

### 5.2 Advanced Analytics
- Career progression analysis
- Industry benchmarking
- Quantitative achievement suggestions

### 5.3 Terminal UX Polish
- Rich terminal output with colors and formatting
- Progress bars and status indicators
- Better error handling and user guidance

## Technical Architecture

### Project Structure
```
src/
├── models/
│   ├── resume.py
│   ├── user_profile.py
│   ├── job_description.py
│   └── resume_problem.py
├── services/
│   ├── content_analysis.py
│   ├── template_service.py
│   ├── job_optimization.py
│   └── llm_integration.py
├── interfaces/
│   ├── terminal_interface.py
│   └── file_handler.py
├── utils/
│   ├── parsers.py
│   ├── validators.py
│   └── formatters.py
├── tests/
│   └── [corresponding test files]
└── main.py
```

### Key Dependencies
- **pydantic**: Data validation and settings
- **python-docx**: Word document processing  
- **PyMuPDF**: PDF processing
- **openai**: LLM integration
- **rich**: Enhanced terminal output
- **click**: CLI framework

### Terminal Application Flow
```
1. Welcome & User Profile Collection
2. Resume File Upload/Parse
3. Initial Analysis & Problem Identification
4. Interactive Gap Filling Session
5. Content Improvement Phase
6. Optional JD Optimization
7. Final Review & Export
```

## Success Criteria by Phase

**Phase 1**: All classes defined with clear interfaces and method signatures
**Phase 2**: Working terminal app that can parse, analyze, and improve a basic resume  
**Phase 3**: Professional-quality content refinement with template intelligence
**Phase 4**: JD optimization provides measurable ATS improvement
**Phase 5**: Robust multi-format support with advanced analytics

## Development Approach

- Test-driven development with comprehensive unit tests
- Modular design allowing for easy feature addition
- Clear separation of concerns between data models, business logic, and interfaces
- Configurable LLM prompts for easy tuning and improvement