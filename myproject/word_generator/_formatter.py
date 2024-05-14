from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

from fpdf import FPDF, drawing

from myproject.word_generator.utils import *
from myproject.word_generator.formatter import Formatter
from myproject.word_generator.game import Game

if TYPE_CHECKING:  # pragma: no cover
    from .game import Puzzle
    from .word import Word
    from .word_search import WordSearch


class WordSearchFormatter(Formatter):
    # pdf export settings
    PDF_TITLE = "Word Search Puzzle"
    PDF_FONT_SIZE_XXL = 18
    PDF_FONT_SIZE_XL = 15
    PDF_FONT_SIZE_L = 12
    PDF_FONT_SIZE_M = 9
    PDF_FONT_SIZE_S = 5
    PDF_PUZZLE_WIDTH = 7  # inches

    def show(
        self,
        game: Game,
        solution: bool = False,
        *args,
        **kwargs,
    ) -> str:
        return self.format_puzzle_for_show(
            game,  # type: ignore
            solution,
        )

    def save(
        self,
        game: Game,
        path: str | Path,
        format: str = "PDF",
        solution: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        if isinstance(path, str):
            path = Path(path)
        saved_file = self.write_pdf_file(
            path,
            game,  # type: ignore
            solution,
        )
        # return saved file path
        return saved_file

    def write_pdf_file(
        self,
        path: Path,
        game: WordSearch,
        solution: bool = False,
        *args,
        **kwargs,
    ) -> Path:
        def draw_puzzle_page(
            pdf: FPDF, game: WordSearch, solution: bool = False
        ) -> FPDF:
            # add a new page and setup the margins
            pdf.add_page()
            pdf.set_margin(0.5)

            # insert the title
            title = "WORD SEARCH" if not solution else "WORD SEARCH (SOLUTION)"
            pdf.set_font("Helvetica", "B", self.PDF_FONT_SIZE_XXL)
            pdf.cell(pdf.epw, 0.25, title,new_y="NEXT", align="C", center=True)
            pdf.ln(0.125)

            # calculate the puzzle size and letter font size
            pdf.set_left_margin(0.75)
            gsize = self.PDF_PUZZLE_WIDTH / game.cropped_size[0]
            gmargin = 0.6875 if gsize > 36 else 0.75
            font_size = int(72 * gsize * gmargin)
            # calculate flexible font size based on word count
            # to ensure all words and the puzzle key fit on one page
            info_font_size = self.PDF_FONT_SIZE_XL - (
                len(game.words) - Game.MIN_PUZZLE_WORDS
            ) * (6 / (Game.MAX_PUZZLE_WORDS - Game.MIN_PUZZLE_WORDS))
            pdf.set_font_size(font_size)

            # get start position of puzzle
            start_x = pdf.get_x()
            start_y = pdf.get_y()

            # draw the puzzle
            for row in game.cropped_puzzle:
                for char in row:
                    pdf.cell(
                        gsize,
                        gsize,
                        char,
                        align="C",
                    )
                pdf.ln(gsize)
            pdf.ln(0.25)

            # draw solution highlights
            if solution:
                for word in game.placed_words:
                    word_start, *_, word_end = word.offset_coordinates(
                        game.bounding_box
                    )
                    word_start_x, word_start_y = word_start
                    word_end_x, word_end_y = word_end

                    # mypy check for word position
                    if (
                        not word_start_x
                        or not word_start_y
                        or not word_end_x
                        or not word_end_y
                    ):
                        continue  # pragma: no cover

                    with pdf.new_path() as path:
                        path.style.fill_color = None
                        path.style.stroke_color = drawing.DeviceRGB(*word.color, 0.5)
                        path.style.stroke_join_style = "round"
                        path.style.stroke_width = pdf.font_size * 0.875
                        path.move_to(
                            start_x + ((word_start_x - 1) * gsize) + (gsize / 2),
                            start_y + ((word_start_y - 1) * gsize) + (gsize / 2),
                        )
                        path.line_to(
                            start_x + ((word_end_x - 1) * gsize) + (gsize / 2),
                            start_y + ((word_end_y - 1) * gsize) + (gsize / 2),
                        )

            # collect puzzle information
            word_list_str = get_word_list_str(game.key)
            LEVEL_DIRS_str = get_LEVEL_DIRS_str(game.level)

            # catch case of all secret words
            if not word_list_str:
                word_list_str = "<ALL SECRET WORDS>"

            # write word list info
            pdf.set_font("Helvetica", "BU", size=info_font_size)
            pdf.cell(
                pdf.epw,
                txt=f"Find words going {LEVEL_DIRS_str}:",
                align="C",
                new_y="NEXT",
            )
            pdf.ln(0.125)

            # write word list
            pdf.set_font("Helvetica", "B", size=info_font_size)
            pdf.set_font_size(info_font_size)
            pdf.set_char_spacing(0.5)

            sorted_words = sorted(game.placed_words, key=lambda w: w.text)
            lines: list[tuple[float, list[Word]]] = []
            line_width = 0.0
            line: list[Word] = []
            for word in sorted_words:
                if word.secret and not solution:
                    continue
                word_cell_width = pdf.get_string_width(word.text) + pdf.c_margin * 4
                if line_width + word_cell_width > pdf.epw:
                    lines.append((line_width, line))
                    line_width = 0.0
                    line = []
                line_width += word_cell_width
                line.append(word)
            if line:
                lines.append((line_width, line))

            for line_width, words in lines:
                line_offset = (pdf.epw - line_width) / 2
                pdf.set_x(pdf.get_x() + line_offset)
                for word in words:
                    if word.secret and not solution:  # pragma: no cover
                        continue
                    start_x = pdf.get_x()
                    start_y = pdf.get_y()
                    word_cell_width = pdf.get_string_width(word.text) + pdf.c_margin * 4
                    pdf.cell(
                        w=word_cell_width,
                        txt=word.text,
                        align="C",
                    )
                    if solution:
                        with pdf.new_path() as path:
                            path.style.fill_color = None
                            path.style.stroke_color = drawing.DeviceRGB(
                                *word.color, 0.5
                            )
                            path.style.stroke_join_style = "round"
                            path.style.stroke_width = pdf.font_size * 0.875
                            path.move_to(
                                start_x + pdf.c_margin * 2.75,
                                start_y + (pdf.font_size / 2),
                            )
                            path.line_to(
                                pdf.get_x() - pdf.c_margin * 2.75,
                                pdf.get_y() + (pdf.font_size / 2),
                            )

                pdf.ln(pdf.font_size * 1.25)

            if not lines and not solution:
                pdf.cell(text="<ALL SECRET WORDS>", align="C", center=True)

            return pdf

        # setup the PDF document
        pdf = FPDF(orientation="P", unit="in", format="Letter")
        pdf.set_title(self.PDF_TITLE)
        pdf.set_line_width(pdf.line_width * 2)

        # draw initial puzzle page
        pdf = draw_puzzle_page(pdf, game)

        # add puzzle solution page if requested
        if solution:
            pdf = draw_puzzle_page(pdf, game, solution)

        # check the provided path since fpdf doesn't offer context manager
        if path.exists():
            raise FileExistsError(f"Sorry, output file '{path}' already exists.")

        # write the final PDF to the filesystem
        try:
            pdf.output(path)
        except OSError:
            raise OSError(f"File could not be saved to '{path}'.")
        return path.absolute()

    def format_puzzle_for_show(
        self,
        game: WordSearch,
        show_solution: bool = False,
    ) -> str:
        word_list_str = get_word_list_str(game.key)
        if show_solution:
            puzzle_list = self.highlight_solution(game)
        else:
            puzzle_list = game.puzzle
        # calculate header length based on cropped puzzle size to account for masks
        header_width = max(
            11, (game.bounding_box[1][0] - game.bounding_box[0][0] + 1) * 2 - 1
        )
        hr = "-" * header_width
        header = hr + "\n" + f"{'WORD SEARCH':^{header_width}}" + "\n" + hr
        puzzle_str = stringify(puzzle_list, game.bounding_box)
        LEVEL_DIRS_str = get_LEVEL_DIRS_str(game.level)
        
        # catch case of all secret words
        if not word_list_str:
            word_list_str = "<ALL SECRET WORDS>"

        output = ""
        output += f"{header}\n"
        output += f"{puzzle_str}\n\n"
        output += f"Find these words: {word_list_str}\n"
        output += f"* Words can go {LEVEL_DIRS_str}\n\n"
        return output

    def highlight_solution(self, game: WordSearch) -> Puzzle:
        """Add highlighting to puzzle solution."""
        output: Puzzle = copy.deepcopy(game.puzzle)
        for word in game.placed_words:
            if (
                word.start_column is None
                or word.start_row is None
                or word.direction is None
            ):  # only here for mypy
                continue  # pragma: no cover
            x = word.start_column
            y = word.start_row
            for char in word.text:
                output[y][x] = f"\u001b[1m\u001b[31m{char}\u001b[0m"
                x += word.direction.c_move
                y += word.direction.r_move
        return output
