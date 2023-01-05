
class SelfPlay:
    def __init__(self, nnet, board) -> None:
        self.model = nnet
        self.board = board
        self.training_data = []
    
    def execute_episode(self):
        """
        Execute one episode of self-play. The game is played until the end, simultaneously 
        collecting training data. when a terminal state is reached, each training example's
        value v is the outcome z of that game from the sample's side's perspective.

        :return: a list of training examples. Form: [s, pi, v] where s is the state represented
        as set of bitboards, pi is the probability distribution returned by MCTS, for v see above.
        """
        pass

    def train(self):
        pass

    