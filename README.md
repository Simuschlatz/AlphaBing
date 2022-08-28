# Xiangqi-AI
![license](https://img.shields.io/github/license/SiiiMiii/Chess-AI)
![activity](https://img.shields.io/github/commit-activity/m/SiiiMiii/Chess-AI)
* Xiangqi is the chinese version of chess very popular amongst East Asian countries.
* This project's final version will be a fairly sophisticated chess engine with built-in AI and the ability to process a physical board

## Table of Contents
* [Featuqres](#features)
* [General Info](#general-information)
* [Screenshots](#screenshots)
* [Dependencies](#dependencies)
* [Project Status](#project-status)
* [To-Dos](#to-dos)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## Features

**Game**
<br/><br/>
_Move Generation_
  * precomputed data + procedual generation
  * move- and attack-maps
  * legal move generation considering pins and blocks
  * handling (multiple) checks, checkmate, stalemate
  <br/>

_UI & UX_<br/>
* basic drag & drop
* rudimentary SFX
* marks possible captures & moves

_AI_
* DONE:
  * minimax algorithm
  * alpha-beta pruning
  * move ordering
  * SHEF (Standard Heuristic Evaluation Function)
* IN PROGRESS:
  * Zobrist Hashing transposition handling
  * SLEF (Self-Learning Evaluation Function): using machine-learning to evaluate positions with a novel method
* TO-DO:
  * iterative deepening
  * position evaluation using CPEF (Combined Position Evaluation Function, weighed sum of SHEF and  SLEF)

**Computer Vision (not implemented yet)**
* supervised learning with tensorflow
* classification on physical board (types & positions)

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
* windows: ```python main.py

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

## Contact
Created by [@SiiiMiii](https://github.com/SiiiMiii) - feel free to contact me at simon.mama07@gmail.com!
