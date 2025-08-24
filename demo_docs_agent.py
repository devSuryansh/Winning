#!/usr/bin/env python3
"""
Google Docs AI Agent Demo

This script demonstrates how to use the Google Docs AI agent to:
1. Create documents with AI-generated content
2. Update existing documents
3. Format documents professionally
4. Create documents from templates
5. Generate content for any topic

Requirements:
- Set PORTIA_API_KEY, JWT_SECRET_KEY, and OPENAI_API_KEY environment variables
- Have the FastAPI server running
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE_URL = "http://localhost:8001/api"


async def demo_google_docs_agent():
    """Demo the Google Docs AI agent functionality"""

    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("❌ Missing OPENAI_API_KEY in .env file")
        return

    user_id = "docs_demo_user"

    print("📄 Google Docs AI Agent Demo")
    print("=" * 60)
    print("🤖 Using AI to create and manage Google Docs")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=120.0) as client:

        # Step 1: Login to get JWT token
        print("\n🔐 Step 1: Authenticating...")
        try:
            login_response = await client.post(
                f"{API_BASE_URL.replace('/api', '')}/auth/login",
                json={"openai_api_key": openai_api_key, "user_id": user_id},
            )

            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.text}")
                return

            login_data = login_response.json()
            token = login_data["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            print(f"✅ Authentication successful!")

        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return

        # Step 2: List available templates and content types
        print(f"\n📋 Step 2: Checking available features...")
        try:
            templates_response = await client.get(
                f"{API_BASE_URL}/docs/templates", headers=headers
            )

            content_types_response = await client.get(
                f"{API_BASE_URL}/docs/content-types", headers=headers
            )

            if templates_response.status_code == 200:
                templates_data = templates_response.json()
                print(f"✅ Available Templates:")
                for category, templates in templates_data["templates"].items():
                    print(
                        f"   🔹 {category.title()}: {', '.join(templates[:3])}{'...' if len(templates) > 3 else ''}"
                    )

            if content_types_response.status_code == 200:
                content_data = content_types_response.json()
                print(f"✅ Available Content Types:")
                for category, types in content_data["content_types"].items():
                    print(
                        f"   🔹 {category.title()}: {', '.join(types[:3])}{'...' if len(types) > 3 else ''}"
                    )

        except Exception as e:
            print(f"❌ Feature check error: {e}")

        # Step 3: Generate content first (to show what the AI can create)
        print(f"\n📝 Step 3: Generating content with AI...")
        try:
            content_response = await client.post(
                f"{API_BASE_URL}/docs/generate-content",
                headers=headers,
                json={
                    "topic": "AI-Powered Project Management Best Practices",
                    "content_type": "technical_documentation",
                    "key_points": [
                        "Automation benefits",
                        "Team collaboration tools",
                        "Performance metrics",
                        "Implementation strategies",
                    ],
                    "tone": "professional",
                    "length": "medium",
                },
            )

            if content_response.status_code == 200:
                content_data = content_response.json()
                print(f"✅ Content Generated:")
                print(f"   🔹 Word Count: {content_data.get('word_count', 'N/A')}")
                if content_data.get("content_outline"):
                    print(
                        f"   🔹 Outline: {', '.join(content_data['content_outline'][:3])}{'...' if len(content_data['content_outline']) > 3 else ''}"
                    )
                if content_data.get("generated_content"):
                    preview = (
                        content_data["generated_content"][:200] + "..."
                        if len(content_data["generated_content"]) > 200
                        else content_data["generated_content"]
                    )
                    print(f"   🔹 Preview: {preview}")
            else:
                print(f"❌ Content generation failed: {content_response.text}")

        except Exception as e:
            print(f"❌ Content generation error: {e}")

        # Step 4: Create a Google Docs document
        print(f"\n📄 Step 4: Creating Google Docs document...")
        created_doc_id = None
        try:
            create_response = await client.post(
                f"{API_BASE_URL}/docs/create-document",
                headers=headers,
                json={
                    "title": "AI-Powered Project Management Guide",
                    "description": "A comprehensive guide on implementing AI tools for project management, including automation strategies, team collaboration, and performance optimization.",
                    "content_type": "technical",
                    "formatting_style": "professional",
                    "include_toc": True,
                    "include_sections": True,
                    "target_length": "medium",
                },
            )

            if create_response.status_code == 200:
                create_data = create_response.json()
                print(f"✅ Document Created:")
                print(f"   🔹 Success: {create_data.get('success')}")
                print(f"   🔹 Title: {create_data.get('doc_title')}")

                if create_data.get("doc_url"):
                    print(f"   🔹 URL: {create_data['doc_url']}")
                    created_doc_id = create_data.get("doc_id")

                if create_data.get("content_preview"):
                    print(f"   🔹 Preview: {create_data['content_preview']}")

                if create_data.get("needs_authentication"):
                    print(f"   🔒 Authentication needed")
                    if create_data.get("oauth_url"):
                        print(f"   🔗 OAuth URL: {create_data['oauth_url']}")

            else:
                print(f"❌ Document creation failed: {create_response.text}")

        except Exception as e:
            print(f"❌ Document creation error: {e}")

        # Step 5: Create a document from template
        print(f"\n📋 Step 5: Creating document from template...")
        try:
            template_response = await client.post(
                f"{API_BASE_URL}/docs/create-from-template",
                headers=headers,
                json={
                    "title": "Weekly Team Meeting Notes - AI Integration",
                    "template_type": "meeting_notes",
                    "variables": {
                        "date": "2025-08-24",
                        "attendees": "Development Team, Project Manager, AI Specialist",
                        "meeting_topic": "AI Integration Progress Review",
                        "agenda_items": [
                            "AI tool evaluation",
                            "Implementation timeline",
                            "Budget review",
                        ],
                    },
                },
            )

            if template_response.status_code == 200:
                template_data = template_response.json()
                print(f"✅ Template Document Created:")
                print(f"   🔹 Success: {template_data.get('success')}")
                print(f"   🔹 Template: {template_data.get('template_used')}")
                print(f"   🔹 Title: {template_data.get('doc_title')}")

                if template_data.get("doc_url"):
                    print(f"   🔹 URL: {template_data['doc_url']}")

                if template_data.get("needs_authentication"):
                    print(f"   🔒 Authentication needed")
                    if template_data.get("oauth_url"):
                        print(f"   🔗 OAuth URL: {template_data['oauth_url']}")
            else:
                print(f"❌ Template document creation failed: {template_response.text}")

        except Exception as e:
            print(f"❌ Template creation error: {e}")

        # Step 6: Quick create example
        print(f"\n⚡ Step 6: Quick document creation...")
        try:
            quick_response = await client.post(
                f"{API_BASE_URL}/docs/quick-create",
                headers=headers,
                params={
                    "title": "AI Development Roadmap 2025",
                    "description": "Strategic roadmap for implementing AI solutions across different business units",
                    "content_type": "business_plan",
                },
            )

            if quick_response.status_code == 200:
                quick_data = quick_response.json()
                print(f"✅ Quick Document Created:")
                print(f"   🔹 Success: {quick_data.get('success')}")
                print(f"   🔹 Title: {quick_data.get('doc_title')}")

                if quick_data.get("doc_url"):
                    print(f"   🔹 URL: {quick_data['doc_url']}")

                if quick_data.get("needs_authentication"):
                    print(f"   🔒 Authentication needed for Google Docs access")

            else:
                print(f"❌ Quick document creation failed: {quick_response.text}")

        except Exception as e:
            print(f"❌ Quick creation error: {e}")

        # Step 7: Update document (if we have a doc ID)
        if created_doc_id:
            print(f"\n📝 Step 7: Updating document...")
            try:
                update_response = await client.post(
                    f"{API_BASE_URL}/docs/update-document",
                    headers=headers,
                    json={
                        "doc_id": created_doc_id,
                        "instructions": "Add a new section about 'AI Ethics and Best Practices' with guidelines for responsible AI implementation",
                        "additional_content": "Include information about bias mitigation, transparency, and accountability in AI systems.",
                    },
                )

                if update_response.status_code == 200:
                    update_data = update_response.json()
                    print(f"✅ Document Updated:")
                    print(f"   🔹 Success: {update_data.get('success')}")
                    if update_data.get("doc_url"):
                        print(f"   🔹 URL: {update_data['doc_url']}")
                else:
                    print(f"❌ Document update failed: {update_response.text}")

            except Exception as e:
                print(f"❌ Document update error: {e}")

    print(f"\n🎉 Demo Complete!")
    print("=" * 60)
    print("💡 What the Google Docs AI agent can do:")
    print("   1. ✅ Create documents with AI-generated content")
    print("   2. ✅ Use professional templates (business, academic, creative)")
    print("   3. ✅ Generate content on any topic with custom requirements")
    print("   4. ✅ Update and modify existing documents")
    print("   5. ✅ Apply professional formatting automatically")
    print("   6. ✅ Handle Google OAuth authentication")
    print("   7. ✅ Support multiple content types and styles")
    print("\n🚀 Next steps:")
    print("   • Visit http://localhost:8001/docs for full API documentation")
    print("   • Try different templates and content types")
    print("   • Integrate with Google OAuth for seamless document creation")


def main():
    """Main function to run the demo"""
    print("Starting Google Docs AI Agent Demo...")
    print("Make sure the FastAPI server is running on port 8001")
    print("-" * 50)

    try:
        asyncio.run(demo_google_docs_agent())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
