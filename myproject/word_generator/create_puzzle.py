from myproject.word_generator.word_search import WordSearch
from myproject.word_generator.create_word import *
from myproject.word_generator.shapes import *
import os

# createPuzzle function to generate word search board
def createPuzzle(course, lesson, grade, shape, level):
    # create puzzle
    words = generate_related_words(course, lesson, grade)
    puzzle = WordSearch(words, level = level)
    if shape == 'circle':
        puzzle.apply_mask(Circle())
    elif shape == 'club':
        puzzle.apply_mask(Club())
    elif shape == 'diamond':
        puzzle.apply_mask(Diamond())
    elif shape == 'donut':
        puzzle.apply_mask(Donut())
    elif shape == 'fish':
        puzzle.apply_mask(Fish())
    elif shape == 'flower':
        puzzle.apply_mask(Flower())
    elif shape == 'hexagon':
        puzzle.apply_mask(Hexagon())
    elif shape == 'heart':
        puzzle.apply_mask(Heart())
    elif shape == 'octagon':
        puzzle.apply_mask(Octagon())
    elif shape == 'pentagon':
        puzzle.apply_mask(Pentagon())
    elif shape == 'spade':
        puzzle.apply_mask(Spade())
    elif shape == 'star5':
        puzzle.apply_mask(Star5())
    elif shape == 'star6':
        puzzle.apply_mask(Star6())
    elif shape == 'star8':
        puzzle.apply_mask(Star8())
    elif shape == 'tree':
        puzzle.apply_mask(Tree())
    elif shape == 'triangle':
        puzzle.apply_mask(Triangle())    
    else:
        pass
    puzzle.show
    return puzzle


# Eg
'''
course = 'math'
lesson = 'plus'
grade = '5'
answer = False
shape = Heart
level = 4
test = createPuzzle(course, lesson, grade, shape, level)
'''