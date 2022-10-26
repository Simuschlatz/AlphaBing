# CheapChess - Combining Algorithmic Powers With The Beauty of Machine Learning
![license](https://img.shields.io/github/license/SiiiMiii/Chess-AI)
![activity](https://img.shields.io/github/commit-activity/m/SiiiMiii/Chess-AI)

## Table of Contents
  - [Features](#features)
  - [General Information](#general-information)
  - [How To Play](#how-to-play)
  - [Screenshots](#screenshots)
  - [Dependencies](#dependencies)
  - [Project Status](#project-status)
  - [Acknowledgements](#acknowledgements)
  - [Contact](#contact)

## Features

**Game**
<br/><br/>
_AI_
* DONE:
  * minimax algorithm
  * alpha-beta pruning
  * move ordering
  * SHEF (Standard Heuristic Evaluation Function) - normal and piece-square-table based
  * Training data collection module for the SLEF model
* IN PROGRESS:
  * Object detection
  * Zobrist Hashing transposition handling
  * SLEF (Self-Learning Evaluation Function): training a model to evaluate positions with data of minimax to further look into the future - **finally got tf installed on ARM chip**
  * multiprocessing
* TO-DO:
  * iterative deepening
  * position evaluation using CPEF (Combined Position Evaluation Function, weighed sum of SHEF and  SLEF)

_Move Generation_
  * precomputed data + procedual generation
  * move- and attack-maps
  * legal move generation considering pins and blocks
  * handling (multiple) checks, pins... - perft results 100% matching consensus
  <br/>


## General-Information
> **What problem does it intend to solve?**
* The initial goal of this project was to compensate for my own very poor skills in Xiangqi with a computer's ability to crunch millions of numbers while getting introduced to simple AI software and Machine Learning.
> **What's the purpose of creating the Project?**
* Artificial Intelligence and especially Machine Learning is very often perceived as this intangibly complicated domain of Computer Science, which is partly true, but not true enough to intimidate people into not even trying to get a fundamental grasp of it.
* With undertaking this project, I want to show that consistently achieving minor goals, making slow but steady progress, can accumulate to exceeding and superceding human brain capacity.
* I want people to know that if a normal 14 y/o, just with the help of a computer and research, can understand and implement the basics of AI and ML, can penetrate the imposing barrier of buzzwords and brainfuck, anyone with the same resources can. * very cliché
* During the process of creation, I also discovered competitions like the national competition of Artificial Intelligence, which have been contributing to my drive of working on this project

## HOW TO PLAY
* clone this repo
* mac: ```python3 main.py```
* windows: ```python main.py```

## Screenshots
<img src="./assets/screenshots/24.08.png" alt="screenshot" width="600"/>

## Dependencies
**To run the current version of the app:**
* python 3
* numpy
* pygame

## Project-Status
Project is: _in progress_

## Acknowledgements
* Inspiration: [@SebLague](https://github.com/SebLague)
* Research done at [chessprogramming wiki](https://www.chessprogramming.org/)
