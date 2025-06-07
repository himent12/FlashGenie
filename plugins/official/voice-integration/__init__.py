"""
Voice Integration Plugin for FlashGenie

Provides text-to-speech and speech-to-text capabilities for hands-free learning
and accessibility support.
"""

import threading
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path

from flashgenie.core.plugin_system import QuizModePlugin
from flashgenie.core.flashcard import Flashcard


class VoiceIntegrationPlugin(QuizModePlugin):
    """Voice integration plugin with TTS and STT capabilities."""
    
    def initialize(self) -> None:
        """Initialize the voice integration plugin."""
        self.require_permission(self.manifest.permissions[0])  # deck_read
        self.require_permission(self.manifest.permissions[1])  # user_data
        self.require_permission(self.manifest.permissions[2])  # system_integration
        
        self.logger.info("Voice Integration plugin initialized")
        
        # Initialize TTS and STT engines
        self.tts_engine = None
        self.stt_recognizer = None
        self.microphone = None
        
        # Voice session state
        self.current_session = None
        self.voice_active = False
        
        # Initialize voice engines
        self._initialize_tts()
        self._initialize_stt()
        
        self.logger.info("Voice engines initialized")
    
    def cleanup(self) -> None:
        """Cleanup voice resources."""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        
        self.voice_active = False
        self.logger.info("Voice Integration plugin cleaned up")
    
    def get_mode_name(self) -> str:
        """Get the name of this quiz mode."""
        return "Voice Learning Mode"
    
    def create_session(self, deck, config: Dict[str, Any]):
        """Create a voice-enabled quiz session."""
        self.logger.info("Creating voice learning session")
        
        session_config = {
            "deck": deck,
            "tts_enabled": self.get_setting("tts_enabled", True),
            "stt_enabled": self.get_setting("stt_enabled", True),
            "auto_speak_questions": self.get_setting("auto_speak_questions", True),
            "auto_speak_answers": self.get_setting("auto_speak_answers", False),
            "voice_timeout": self.get_setting("voice_timeout", 5),
            **config
        }
        
        self.current_session = VoiceQuizSession(self, session_config)
        return self.current_session
    
    def get_settings_schema(self) -> Dict[str, Any]:
        """Get settings schema for this quiz mode."""
        return self.manifest.settings_schema
    
    def _initialize_tts(self) -> None:
        """Initialize text-to-speech engine."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            rate = self.get_setting("voice_rate", 150)
            volume = self.get_setting("voice_volume", 0.8)
            
            self.tts_engine.setProperty('rate', rate)
            self.tts_engine.setProperty('volume', volume)
            
            # Set voice gender if available
            voices = self.tts_engine.getProperty('voices')
            if voices:
                gender_pref = self.get_setting("voice_gender", "auto")
                if gender_pref != "auto":
                    for voice in voices:
                        if gender_pref.lower() in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            
            self.logger.info("TTS engine initialized successfully")
            
        except ImportError:
            self.logger.warning("pyttsx3 not available - TTS disabled")
            self.tts_engine = None
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
    
    def _initialize_stt(self) -> None:
        """Initialize speech-to-text engine."""
        try:
            import speech_recognition as sr
            self.stt_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.stt_recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("STT engine initialized successfully")
            
        except ImportError:
            self.logger.warning("SpeechRecognition not available - STT disabled")
            self.stt_recognizer = None
        except Exception as e:
            self.logger.error(f"Failed to initialize STT: {e}")
            self.stt_recognizer = None
    
    def speak_text(self, text: str, blocking: bool = False) -> None:
        """Convert text to speech."""
        if not self.tts_engine or not self.get_setting("tts_enabled", True):
            return
        
        try:
            # Clean text for better speech
            clean_text = self._clean_text_for_speech(text)
            
            if blocking:
                self.tts_engine.say(clean_text)
                self.tts_engine.runAndWait()
            else:
                # Non-blocking speech
                def speak():
                    self.tts_engine.say(clean_text)
                    self.tts_engine.runAndWait()
                
                thread = threading.Thread(target=speak, daemon=True)
                thread.start()
            
            self.logger.debug(f"Speaking: {clean_text[:50]}...")
            
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
    
    def listen_for_speech(self, timeout: Optional[int] = None) -> Optional[str]:
        """Listen for speech input and convert to text."""
        if not self.stt_recognizer or not self.get_setting("stt_enabled", True):
            return None
        
        timeout = timeout or self.get_setting("voice_timeout", 5)
        language = self.get_setting("language", "en-US")
        
        try:
            with self.microphone as source:
                self.logger.debug("Listening for speech...")
                audio = self.stt_recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech
            text = self.stt_recognizer.recognize_google(audio, language=language)
            self.logger.debug(f"Recognized: {text}")
            return text
            
        except Exception as e:
            self.logger.debug(f"STT error: {e}")
            return None
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis."""
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Replace common symbols
        replacements = {
            '&': 'and',
            '@': 'at',
            '#': 'number',
            '%': 'percent',
            '+': 'plus',
            '=': 'equals',
            '<': 'less than',
            '>': 'greater than',
            '→': 'leads to',
            '←': 'comes from'
        }
        
        for symbol, word in replacements.items():
            text = text.replace(symbol, f' {word} ')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Get current voice system status."""
        return {
            "tts_available": self.tts_engine is not None,
            "stt_available": self.stt_recognizer is not None,
            "tts_enabled": self.get_setting("tts_enabled", True),
            "stt_enabled": self.get_setting("stt_enabled", True),
            "voice_active": self.voice_active,
            "current_session": self.current_session is not None,
            "language": self.get_setting("language", "en-US"),
            "voice_rate": self.get_setting("voice_rate", 150),
            "voice_volume": self.get_setting("voice_volume", 0.8)
        }


class VoiceQuizSession:
    """Voice-enabled quiz session."""
    
    def __init__(self, plugin: VoiceIntegrationPlugin, config: Dict[str, Any]):
        self.plugin = plugin
        self.config = config
        self.deck = config["deck"]
        self.current_card = None
        self.session_stats = {
            "cards_reviewed": 0,
            "voice_responses": 0,
            "speech_recognition_accuracy": 0.0
        }
        
        self.plugin.logger.info("Voice quiz session created")
    
    def start_session(self) -> None:
        """Start the voice quiz session."""
        self.plugin.voice_active = True
        
        if self.config.get("tts_enabled"):
            welcome_msg = f"Starting voice learning session for {self.deck.name}. You can speak your answers or use keyboard input."
            self.plugin.speak_text(welcome_msg)
        
        self.plugin.logger.info("Voice quiz session started")
    
    def present_card(self, card: Flashcard) -> None:
        """Present a flashcard with voice support."""
        self.current_card = card
        
        # Display question
        print(f"\n📝 Question: {card.question}")
        
        # Speak question if enabled
        if self.config.get("auto_speak_questions", True):
            self.plugin.speak_text(card.question)
        
        # Wait for user response
        self._get_user_response()
    
    def _get_user_response(self) -> None:
        """Get user response via voice or keyboard."""
        if not self.current_card:
            return
        
        print("\n🎤 Speak your answer, press Enter to reveal, or type 'voice' to use voice commands:")
        
        # Try voice input first if enabled
        if self.config.get("stt_enabled", True):
            print("🔊 Listening... (speak now)")
            voice_response = self.plugin.listen_for_speech()
            
            if voice_response:
                print(f"🎤 You said: {voice_response}")
                self.session_stats["voice_responses"] += 1
                
                # Simple answer checking
                similarity = self._calculate_similarity(voice_response, self.current_card.answer)
                
                if similarity > 0.6:
                    print("✅ Good! Your voice answer seems correct.")
                    if self.config.get("auto_speak_answers", False):
                        self.plugin.speak_text("Correct! " + self.current_card.answer)
                else:
                    print("🤔 Let me show you the correct answer:")
                    self._reveal_answer()
            else:
                print("🔇 No speech detected. Press Enter to reveal answer:")
                input()
                self._reveal_answer()
        else:
            # Keyboard input only
            user_input = input().strip().lower()
            if user_input == "voice":
                self._handle_voice_commands()
            else:
                self._reveal_answer()
        
        self.session_stats["cards_reviewed"] += 1
    
    def _reveal_answer(self) -> None:
        """Reveal the answer with voice support."""
        if not self.current_card:
            return
        
        print(f"\n💡 Answer: {self.current_card.answer}")
        
        # Speak answer if enabled
        if self.config.get("auto_speak_answers", False):
            self.plugin.speak_text(self.current_card.answer)
    
    def _calculate_similarity(self, response: str, answer: str) -> float:
        """Calculate similarity between voice response and correct answer."""
        # Simple similarity calculation
        response_words = set(response.lower().split())
        answer_words = set(answer.lower().split())
        
        if not answer_words:
            return 0.0
        
        intersection = response_words.intersection(answer_words)
        return len(intersection) / len(answer_words)
    
    def _handle_voice_commands(self) -> None:
        """Handle voice commands."""
        print("🎤 Voice commands available:")
        print("  - 'repeat question' - Repeat the current question")
        print("  - 'speak answer' - Hear the answer")
        print("  - 'next card' - Move to next card")
        print("  - 'session stats' - Hear session statistics")
        
        command = self.plugin.listen_for_speech(timeout=10)
        
        if command:
            command = command.lower()
            
            if "repeat" in command and "question" in command:
                self.plugin.speak_text(self.current_card.question)
            elif "speak" in command and "answer" in command:
                self.plugin.speak_text(self.current_card.answer)
                self._reveal_answer()
            elif "next" in command:
                print("Moving to next card...")
            elif "stats" in command:
                self._speak_session_stats()
            else:
                self.plugin.speak_text("Command not recognized. Please try again.")
    
    def _speak_session_stats(self) -> None:
        """Speak current session statistics."""
        stats_text = f"Session statistics: {self.session_stats['cards_reviewed']} cards reviewed, {self.session_stats['voice_responses']} voice responses given."
        self.plugin.speak_text(stats_text)
        print(f"📊 {stats_text}")
    
    def end_session(self) -> Dict[str, Any]:
        """End the voice quiz session."""
        self.plugin.voice_active = False
        
        if self.config.get("tts_enabled"):
            summary = f"Voice session completed. You reviewed {self.session_stats['cards_reviewed']} cards with {self.session_stats['voice_responses']} voice responses."
            self.plugin.speak_text(summary)
        
        self.plugin.logger.info("Voice quiz session ended")
        return self.session_stats
