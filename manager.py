import argparse
import multiprocessing as mp

def init_parser():
    program_descr = "A Program to train a Deep Neural Network with data gathered from self-play, \
        to evaluate the network, to combine it with traditional alpha-beta-search and ultimately \
        to improve knowledge about the domain on Xiangqi."

    parser = argparse.ArgumentParser(prog="main.py",
                                    description=program_descr,
                                    epilog="Have fun ;)")

    parser.add_argument("agent", type=str, nargs="?", default="ab", choices=["ab", "az", "abz"],
                        help="AI-agent playing in interactive environment \
                            (ab: Alpha-Beta, az: AlphaZero, abz: Alpha-Beta-Zero) \
                            (default: ab)")
    parser.add_argument("cores", type=int, nargs="?", default=mp.cpu_count(),
                        help="maximum number of processors to use for pipeline \
                            (default: multiprocessing.cpu_count())")
    parser.add_argument("time", type=int, nargs="?", default=5,
                        help="time on the clock in minutes (default: 5)")

    parser.add_argument("--chinese", dest="chinese_style", action="store_true", 
                        help="rendering chinese style UI")
    parser.add_argument("--perft", dest="run_perft", action="store_true",
                        help="run performance tests for move generation speed and accuracy")
    parser.add_argument("--pipeline", dest="run_pipeline", action="store_true",
                        help="run the self-play and training pipeline (to evaluate, see --eval)")
    parser.add_argument("--eval", dest="evaluate", action="store_true",
                        help="add evaluation to the pipeline")
    parser.add_argument("--nui", dest="no_ui", action="store_true",
                        help="no UI")
    parser.add_argument("--black",  dest="play_as_black", action="store_true",
                        help="play black")
    parser.add_argument("--second",  dest="move_second", action="store_true",
                        help="move second")
    return parser

def get_config():
    parser = init_parser()
    args = parser.parse_args()
    return args

config = get_config()