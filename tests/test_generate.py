import unittest
from src.generate import build_context_string, generate_answer


class TestGenerate(unittest.TestCase):
    def test_build_context_string(self):
        retrieved_results = [
            {
                "chunk": {"id": 1, "text": "This is context one."},
                "score": 0.85
            },
            {
                "chunk": {"id": 2, "text": "This is context two."},
                "score": 0.65
            }
        ]
        context_str = build_context_string(retrieved_results)
        
        self.assertIn("[Source Chunk #1 (Relevance Score: 0.85)]:", context_str)
        self.assertIn("This is context one.", context_str)
        self.assertIn("[Source Chunk #2 (Relevance Score: 0.65)]:", context_str)
        self.assertIn("This is context two.", context_str)

    def test_generate_answer_irrelevant(self):
        answer = generate_answer(
            query="test query",
            retrieved_results=[],
            is_relevant=False
        )
        self.assertEqual(answer, "I cannot find any relevant information in the uploaded document to answer your question.")

    def test_generate_answer_mock_mode(self):
        retrieved_results = [
            {
                "chunk": {"id": 4, "text": "ACME Corporation offers gym reimbursement of $50 per month."},
                "score": 0.90
            }
        ]
        # In offline/mock mode (no key), it should return the mock answer format
        answer = generate_answer(
            query="how much is gym reimbursement?",
            retrieved_results=retrieved_results,
            is_relevant=True,
            provider="mock"
        )
        
        self.assertIn("[Demo / Offline Mode - No LLM API Key set]", answer)
        self.assertIn("Chunk #4", answer)
        self.assertIn("ACME Corporation offers gym reimbursement", answer)


if __name__ == "__main__":
    unittest.main()
