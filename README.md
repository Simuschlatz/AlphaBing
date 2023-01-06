# CheapChess - making complex software accessible for everyone
![license](https://img.shields.io/github/license/SiiiMiii/Chess-AI)
![activity](https://img.shields.io/github/commit-activity/m/SiiiMiii/Chess-AI)

> Combining Algorithmic Powers With The Beauty of Machine Learning


- [CheapChess - making complex software accessible for everyone](#cheapchess---making-complex-software-accessible-for-everyone)
  - [Features](#features)
  - [Installation](#installation)
  - [Gameplay](#gameplay)
  - [Dependencies](#dependencies)

## Features
**Move Generation**
* precomputed data + procedual generation - the fastest worldwide
* move- and attack-maps
* legal move generation considering pins and blocks
* handling (multiple) checks, pins... with 100% accuracy
<br></br>

**State of the art search method**
* _DONE:_
  * minimax algorithm
  * alpha-beta pruning
  * multiprocessing
  * move ordering
  * SHEF (Standard Heuristic Evaluation Function) - normal and piece-square-table based
  * Training data collection module for the SLEF model
* _IN PROGRESS:_
  * Object detection
  * Zobrist Hashing transposition handling
* _TO-DO_
  * iterative deepening

**AlphaZero based approach**
* _FINISHED:_
  * Convolutional RNN Model
  * Bitboard utility
  * self-play
    * Monte Carlo Tree Search (MCTS)
    * reinforcement learning
      * training data collection (through self-play)
      * training model
* _IN PROGRESS:_
  * Alpha-Beta optimization for MCTS
* _To-DO:_
* optimization and JIT compiler support
* Human vs. AI

## Installation
* clone this repo ```git clone https://github.com/Simuschlatz/CheapChess.git```
* run main file ```python3 main.py``` or ```python main.py```

    |Key|function|
    |---|--------|
    |space|unmake previous move|
    |a|watch ai play against itself|
    |c|listen for speech commands|

## Gameplay
![Gameplay](./assets/screenshots/gameplay.gif)

## Dependencies
**To run the current version of the app:**
* python 3
* numpy
* pandas
* tensorflow
* keras
* pygame

**For speech-to-text commands:**
* Pyaudio
* SpeechRecognition

_requirements file will be added soon_
