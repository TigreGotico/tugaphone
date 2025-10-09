"""multilingual phonemizers"""

import json
import os
from langcodes import tag_distance
import subprocess
from typing import List, Dict, Optional

import numpy as np
import onnxruntime
import requests


class EspeakError(Exception):
    """Custom exception for espeak-ng related errors."""
    pass


class EspeakPhonemizer:
    """
    A phonemizer class that uses the espeak-ng command-line tool to convert text into phonemes.
    It segments the input text heuristically based on punctuation to mimic clause-by-clause processing.
    """
    ESPEAK_LANGS = ['es-419', 'ca', 'qya', 'ga', 'et', 'ky', 'io', 'fa-latn', 'en-gb', 'fo', 'haw', 'kl',
                    'ta', 'ml', 'gd', 'sd', 'es', 'hy', 'ur', 'ro', 'hi', 'or', 'ti', 'ca-va', 'om', 'tr', 'pa',
                    'smj', 'mk', 'bg', 'cv', "fr", 'fi', 'en-gb-x-rp', 'ru', 'mt', 'an', 'mr', 'pap', 'vi', 'id',
                    'fr-be', 'ltg', 'my', 'nl', 'shn', 'ba', 'az', 'cmn', 'da', 'as', 'sw',
                    'piqd', 'en-us', 'hr', 'it', 'ug', 'th', 'mi', 'cy', 'ru-lv', 'ia', 'tt', 'hu', 'xex', 'te', 'ne',
                    'eu', 'ja', 'bpy', 'hak', 'cs', 'en-gb-scotland', 'hyw', 'uk', 'pt', 'bn', 'mto', 'yue',
                    'be', 'gu', 'sv', 'sl', 'cmn-latn-pinyin', 'lfn', 'lv', 'fa', 'sjn', 'nog', 'ms',
                    'vi-vn-x-central', 'lt', 'kn', 'he', 'qu', 'ca-ba', 'quc', 'nb', 'sk', 'tn', 'py', 'si', 'de',
                    'ar', 'en-gb-x-gbcwmd', 'bs', 'qdb', 'sq', 'sr', 'tk', 'en-029', 'ht', 'ru-cl', 'af', 'pt-br',
                    'fr-ch', 'ka', 'en-gb-x-gbclan', 'ko', 'is', 'ca-nw', 'gn', 'kok', 'la', 'lb', 'am', 'kk', 'ku',
                    'kaa', 'jbo', 'eo', 'uz', 'nci', 'vi-vn-x-south', 'el', 'pl', 'grc', ]

    @classmethod
    def get_lang(cls, target_lang: str) -> str:
        """
        Validates and returns the closest supported language code.

        Args:
            target_lang (str): The language code to validate.

        Returns:
            str: The validated language code.

        Raises:
            ValueError: If the language code is unsupported.
        """
        if target_lang.lower() == "en-gb":
            return "en-gb-x-rp"
        if target_lang in cls.ESPEAK_LANGS:
            return target_lang
        if target_lang.lower().split("-")[0] in cls.ESPEAK_LANGS:
            return target_lang.lower().split("-")[0]
        return cls.match_lang(target_lang, cls.ESPEAK_LANGS)

    @staticmethod
    def match_lang(target_lang: str, valid_langs: List[str]) -> str:
        """
        Validates and returns the closest supported language code.

        Args:
            target_lang (str): The language code to validate.

        Returns:
            str: The validated language code.

        Raises:
            ValueError: If the language code is unsupported.
        """
        if target_lang in valid_langs:
            return target_lang
        best_lang = "und"
        best_distance = 10000000
        for l in valid_langs:
            try:
                distance: int = tag_distance(l, target_lang)
            except:
                try:
                    l = f"{l.split('-')[0]}-{l.split('-')[1]}"
                    distance: int = tag_distance(l, target_lang)
                except:
                    try:
                        distance: int = tag_distance(l.split('-')[0], target_lang)
                    except:
                        continue
            if distance < best_distance:
                best_lang, best_distance = l, distance

        # If the score is low (meaning a good match), return the language
        if best_distance <= 10:
            return best_lang
        # Otherwise, raise an error for unsupported language
        raise ValueError(f"unsupported language code: {target_lang}")

    @staticmethod
    def _run_espeak_command(args: List[str], input_text: str = None, check: bool = True) -> str:
        """
        Helper function to run espeak-ng commands via subprocess.
        Executes 'espeak-ng' with the given arguments and input text.
        Captures stdout and stderr, and raises EspeakError on failure.

        Args:
            args (List[str]): A list of command-line arguments for espeak-ng.
            input_text (str, optional): The text to pass to espeak-ng's stdin. Defaults to None.
            check (bool, optional): If True, raises a CalledProcessError if the command returns a non-zero exit code. Defaults to True.

        Returns:
            str: The stripped standard output from the espeak-ng command.

        Raises:
            EspeakError: If espeak-ng command is not found, or if the subprocess call fails.
        """
        command: List[str] = ['espeak-ng'] + args
        try:
            process: subprocess.CompletedProcess = subprocess.run(
                command,
                input=input_text,
                capture_output=True,
                text=True,
                check=check,
                encoding='utf-8',
                errors='replace'  # Replaces unencodable characters with a placeholder
            )
            return process.stdout.strip()
        except FileNotFoundError:
            raise EspeakError(
                "espeak-ng command not found. Please ensure espeak-ng is installed "
                "and available in your system's PATH."
            )
        except subprocess.CalledProcessError as e:
            raise EspeakError(
                f"espeak-ng command failed with error code {e.returncode}:\n"
                f"STDOUT: {e.stdout}\n"
                f"STDERR: {e.stderr}"
            )
        except Exception as e:
            raise EspeakError(f"An unexpected error occurred while running espeak-ng: {e}")

    def phonemize(self, text: str, lang: str) -> str:
        lang = self.get_lang(lang)
        return self._run_espeak_command(
            ['-q', '-x', '--ipa', '-v', lang],
            input_text=text
        ).replace("\n", " . ")




if __name__ == "__main__":

    espeak = EspeakPhonemizer()

    lang = "en-gb"

    text1 = "Hello, world. How are you?"

    print("\n--- Getting phonemes for 'Hello, world. How are you?' ---")
    phonemes1 = espeak.phonemize(text1, lang)

    print(f" Espeak  Phonemes: {phonemes1}")


