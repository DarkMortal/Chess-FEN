from PIL import Image
import unittest
from main import generate_board_matrix, matrix_to_fen

IMAGE_SIZE = (1024, 1024) 
pre_process = lambda image_source: Image.open(image_source).convert("RGB").resize(IMAGE_SIZE)

def helper(img_src: str, is_flipped: bool) -> str:
    img = pre_process(image_source = img_src)
    board_matrix = generate_board_matrix(img)

    # Base FEN
    if is_flipped:
        board_matrix = [row[::-1] for row in board_matrix[::-1]]
    
    return matrix_to_fen(board_matrix)

test_results = [
    "4krnr/p5Q1/1pp1p3/3p1pP1/3P4/3N4/PPP1N1PP/R4RK1",
    "7k/1bp3pp/3p4/1P1P1p2/3q4/1R4P1/2QBr2P/3R3K",
    "rn1qkbnr/1pp2ppp/p2p4/4N3/2B1P1b1/2N5/PPPP1PPP/R1BQK2R",
    "7k/2p3pp/3p4/1P1b1p2/3q4/1R4P1/2QBr2P/3R3K",
    "4rrk1/ppp1bppp/3q1n2/4n3/2B1P1b1/1PP1QN2/PB1N1PPP/R4RK1",
    "r4r1k/5ppp/p2p4/1p3N2/3QP1n1/P2P4/1P2KPq1/R3R3"
]

class Test_Default(unittest.TestCase):

    def test_example1(self):
        result = helper("tests/Example 1.png", False)
        self.assertEqual(result, test_results[0])

    def test_example2(self):
        result = helper("tests/Example 2.png", False)
        self.assertEqual(result, test_results[1])

    def test_example3(self):
        result = helper("tests/Example 3.png", False)
        self.assertEqual(result, test_results[2])

    def test_example6(self):
        result = helper("tests/Example 6.png", False)
        self.assertEqual(result, test_results[5])

class Test_Flipped(unittest.TestCase):

    def test_example4(self):
        result = helper("tests/Example 4.png", True)
        self.assertEqual(result, test_results[3])

    def test_example5(self):
        result = helper("tests/Example 5.png", True)
        self.assertEqual(result, test_results[4])

# driver code
if __name__ == "__main__":
    unittest.main()