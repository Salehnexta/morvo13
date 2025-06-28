from app.api.v1.endpoints.chat import generate_simple_response


def test_generate_simple_response_branches() -> None:
    # Greeting branch
    resp = generate_simple_response("Hi there!")
    assert "hello" in resp.lower()

    # SEO branch
    resp = generate_simple_response("I want better google ranking")
    assert "seo" in resp.lower()

    # Marketing branch
    resp = generate_simple_response("Need a marketing strategy")
    assert "marketing" in resp.lower()

    # Competitor branch
    resp = generate_simple_response("competitor analysis please")
    assert "competitor" in resp.lower()

    # Default branch
    resp = generate_simple_response("random unrelated text")
    assert "ai marketing assistant" in resp.lower() 