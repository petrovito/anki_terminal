import pytest
from pathlib import Path
from template_manager import TemplateManager

def test_get_builtin_template_path():
    """Test getting path to built-in template."""
    manager = TemplateManager()
    
    # Test with .html extension
    path = manager.get_builtin_template_path("jap_anime_question.html")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_question.html"
    
    # Test without .html extension
    path = manager.get_builtin_template_path("jap_anime_question")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_question.html"
    
    # Test CSS file
    path = manager.get_builtin_template_path("jap_anime_style.css")
    assert path is not None
    assert path.exists()
    assert path.name == "jap_anime_style.css"
    
    # Test non-existent template
    path = manager.get_builtin_template_path("nonexistent")
    assert path is None

def test_resolve_template_path(tmp_path):
    """Test resolving template paths."""
    manager = TemplateManager()
    
    # Test built-in template
    path = manager.resolve_template_path("jap_anime_question")
    assert path.exists()
    assert path.name == "jap_anime_question.html"
    
    # Test filesystem path
    test_template = tmp_path / "test_template.html"
    test_template.write_text("{{Test}}")
    path = manager.resolve_template_path(str(test_template))
    assert path.exists()
    assert path == test_template
    
    # Test non-existent template
    with pytest.raises(ValueError, match="Template file not found"):
        manager.resolve_template_path("nonexistent")

def test_load_template(tmp_path):
    """Test loading template contents."""
    manager = TemplateManager()
    
    # Test loading built-in template
    content = manager.load_template("jap_anime_question")
    assert "{{Japanese}}" in content
    assert "{{#Audio}}" in content
    
    # Test loading CSS file
    content = manager.load_template("jap_anime_style.css")
    assert ".card {" in content
    assert ".english {" in content
    assert ".context {" in content
    
    # Test loading filesystem template
    test_content = "{{Custom}}\n{{Template}}"
    test_template = tmp_path / "test_template.html"
    test_template.write_text(test_content)
    loaded_content = manager.load_template(str(test_template))
    assert loaded_content == test_content.strip()
    
    # Test invalid template
    with pytest.raises(ValueError, match="Error loading template"):
        manager.load_template("nonexistent.html")

def test_template_whitespace_handling():
    """Test that template loading properly handles whitespace."""
    manager = TemplateManager()
    
    # Create test templates with different whitespace patterns
    templates = {
        "no_whitespace": "{{Test}}",
        "leading_whitespace": "  {{Test}}",
        "trailing_whitespace": "{{Test}}  ",
        "empty_lines": "\n{{Test}}\n\n",
        "mixed_whitespace": "  {{Test}}  \n  {{More}}  "
    }
    
    for name, content in templates.items():
        # Create temporary file
        path = Path(manager.builtin_templates_dir) / f"{name}.html"
        path.write_text(content)
        
        # Load and verify
        loaded = manager.load_template(str(path))
        assert loaded == content.strip()
        
        # Clean up
        path.unlink() 