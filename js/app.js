/**
 * French Learning App - Main Application Logic
 * 1st Year Primary School - Tunisia
 */

(function () {
    "use strict";

    // ========== State ==========
    let currentLesson = null;
    let currentWordIndex = 0;
    let quizQuestions = [];
    let currentQuizIndex = 0;
    let quizScore = 0;
    let scores = loadScores();

    // ========== DOM Elements ==========
    const $ = (id) => document.getElementById(id);
    const homeScreen = $("home-screen");
    const lessonScreen = $("lesson-screen");
    const lessonsGrid = $("lessons-grid");

    // Vocab elements
    const vocabMode = $("vocab-mode");
    const quizMode = $("quiz-mode");
    const resultsMode = $("results-mode");
    const vocabCard = $("vocab-card");
    const vocabImage = $("vocab-image");
    const vocabFrench = $("vocab-french");
    const vocabPhonetic = $("vocab-phonetic");
    const vocabArabic = $("vocab-arabic");
    const vocabCounter = $("vocab-counter");
    const btnPrev = $("btn-prev");
    const btnNext = $("btn-next");
    const btnSound = $("btn-sound");
    const btnStartQuiz = $("btn-start-quiz");
    const btnBack = $("btn-back");
    const lessonTitle = $("lesson-title");
    const progressFill = $("progress-fill");

    // Quiz elements
    const quizQuestion = $("quiz-question");
    const quizPrompt = $("quiz-prompt");
    const quizOptions = $("quiz-options");
    const quizFeedback = $("quiz-feedback");
    const btnNextQuestion = $("btn-next-question");

    // Results elements
    const resultsEmoji = $("results-emoji");
    const resultsTitle = $("results-title");
    const resultsSubtitle = $("results-subtitle");
    const resultsScore = $("results-score");
    const resultsStars = $("results-stars");
    const btnRetry = $("btn-retry");
    const btnHomeResults = $("btn-home-results");

    // ========== Score Persistence ==========
    function loadScores() {
        try {
            return JSON.parse(localStorage.getItem("frenchAppScores")) || {};
        } catch {
            return {};
        }
    }

    function saveScore(lessonId, score, total) {
        const pct = Math.round((score / total) * 100);
        const existing = scores[lessonId] || 0;
        if (pct > existing) {
            scores[lessonId] = pct;
            localStorage.setItem("frenchAppScores", JSON.stringify(scores));
        }
    }

    function getStars(pct) {
        if (pct >= 90) return "⭐⭐⭐";
        if (pct >= 60) return "⭐⭐";
        if (pct >= 30) return "⭐";
        return "";
    }

    // ========== Render Home ==========
    function renderHome() {
        lessonsGrid.innerHTML = "";
        LESSONS.forEach((lesson) => {
            const card = document.createElement("div");
            card.className = "lesson-card";
            const pct = scores[lesson.id] || 0;
            const stars = getStars(pct);
            card.innerHTML = `
                <span class="card-emoji">${lesson.emoji}</span>
                <div class="card-title-fr">${lesson.titleFr}</div>
                <div class="card-title-ar">${lesson.titleAr}</div>
                <div class="card-count">${lesson.words.length} mots - ${lesson.words.length} كلمات</div>
                ${stars ? `<div class="card-stars">${stars}</div>` : ""}
            `;
            card.addEventListener("click", () => openLesson(lesson));
            lessonsGrid.appendChild(card);
        });
    }

    // ========== Navigation ==========
    function showScreen(screen) {
        homeScreen.classList.remove("active");
        lessonScreen.classList.remove("active");
        screen.classList.add("active");
        window.scrollTo(0, 0);
    }

    function showMode(mode) {
        vocabMode.classList.remove("active");
        quizMode.classList.remove("active");
        resultsMode.classList.remove("active");
        mode.classList.add("active");
    }

    // ========== Lesson ==========
    function openLesson(lesson) {
        currentLesson = lesson;
        currentWordIndex = 0;
        lessonTitle.textContent = `${lesson.emoji} ${lesson.titleFr} - ${lesson.titleAr}`;
        showScreen(lessonScreen);
        showMode(vocabMode);
        renderWord();
    }

    function renderWord() {
        const word = currentLesson.words[currentWordIndex];
        const total = currentLesson.words.length;

        vocabImage.textContent = word.emoji;
        vocabFrench.textContent = word.fr;
        vocabPhonetic.textContent = `[ ${word.phonetic} ]`;
        vocabArabic.textContent = word.ar;
        vocabCounter.textContent = `${currentWordIndex + 1} / ${total}`;

        btnPrev.disabled = currentWordIndex === 0;
        btnNext.disabled = currentWordIndex === total - 1;

        // Progress
        const pct = ((currentWordIndex + 1) / total) * 100;
        progressFill.style.width = pct + "%";

        // Animate card
        vocabCard.style.animation = "none";
        // Force reflow
        void vocabCard.offsetHeight;
        vocabCard.style.animation = "fadeIn 0.4s ease";
    }

    // ========== Text-to-Speech ==========
    function speakFrench(text) {
        if (!("speechSynthesis" in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "fr-FR";
        utterance.rate = 0.8;
        utterance.pitch = 1.1;
        window.speechSynthesis.speak(utterance);
    }

    // ========== Quiz ==========
    function startQuiz() {
        quizScore = 0;
        currentQuizIndex = 0;
        quizQuestions = generateQuizQuestions(currentLesson);
        showMode(quizMode);
        renderQuizQuestion();
    }

    function generateQuizQuestions(lesson) {
        const words = [...lesson.words];
        const questions = [];

        // Shuffle words
        for (let i = words.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [words[i], words[j]] = [words[j], words[i]];
        }

        // Take up to 8 questions
        const selected = words.slice(0, 8);

        selected.forEach((word) => {
            // Generate wrong options from the same lesson
            const others = lesson.words
                .filter((w) => w.fr !== word.fr)
                .sort(() => Math.random() - 0.5)
                .slice(0, 3);

            const type = lesson.quizType || "fr-to-ar";

            if (type === "fr-to-ar") {
                const options = [...others.map((w) => w.ar), word.ar].sort(
                    () => Math.random() - 0.5
                );
                questions.push({
                    questionAr: "ما معنى هذه الكلمة بالعربية؟",
                    questionFr: "Que signifie ce mot ?",
                    prompt: word.fr,
                    promptEmoji: word.emoji,
                    options: options,
                    correct: word.ar,
                    type: "text",
                });
            } else {
                const options = [...others.map((w) => w.fr), word.fr].sort(
                    () => Math.random() - 0.5
                );
                questions.push({
                    questionAr: "ما اسم هذا بالفرنسية؟",
                    questionFr: "Comment dit-on ?",
                    prompt: word.emoji,
                    promptEmoji: "",
                    options: options,
                    correct: word.fr,
                    type: "text",
                });
            }
        });

        return questions;
    }

    function renderQuizQuestion() {
        const q = quizQuestions[currentQuizIndex];

        quizQuestion.textContent = `${q.questionAr} - ${q.questionFr}`;

        if (q.promptEmoji && q.prompt !== q.promptEmoji) {
            quizPrompt.innerHTML = `<span style="font-size:2.5rem">${q.promptEmoji}</span><br>${q.prompt}`;
        } else {
            quizPrompt.textContent = q.prompt;
        }

        quizOptions.innerHTML = "";
        quizFeedback.textContent = "";
        quizFeedback.className = "quiz-feedback";
        btnNextQuestion.classList.add("hidden");

        const progressPct =
            ((currentQuizIndex + 1) / quizQuestions.length) * 100;
        progressFill.style.width = progressPct + "%";

        q.options.forEach((option) => {
            const btn = document.createElement("button");
            btn.className = "quiz-option";
            btn.textContent = option;

            // Set Arabic font for Arabic options
            if (/[\u0600-\u06FF]/.test(option)) {
                btn.style.fontFamily = "var(--font-ar)";
                btn.style.direction = "rtl";
            }

            btn.addEventListener("click", () => handleAnswer(btn, option, q));
            quizOptions.appendChild(btn);
        });
    }

    function handleAnswer(btn, selected, question) {
        // Disable all options
        document.querySelectorAll(".quiz-option").forEach((b) => {
            b.classList.add("disabled");
            if (b.textContent === question.correct) {
                b.classList.add("correct");
            }
        });

        if (selected === question.correct) {
            btn.classList.add("correct");
            quizScore++;
            quizFeedback.textContent = "!أحسنت! 🎉 - Bravo";
            quizFeedback.className = "quiz-feedback correct";
            speakFrench(
                question.type === "text" && !/[\u0600-\u06FF]/.test(selected)
                    ? selected
                    : question.prompt
            );
        } else {
            btn.classList.add("wrong");
            quizFeedback.innerHTML = `❌ الإجابة الصحيحة: <strong>${question.correct}</strong>`;
            quizFeedback.className = "quiz-feedback wrong";
        }

        if (currentQuizIndex < quizQuestions.length - 1) {
            btnNextQuestion.classList.remove("hidden");
        } else {
            setTimeout(showResults, 1500);
        }
    }

    function showResults() {
        const total = quizQuestions.length;
        const pct = Math.round((quizScore / total) * 100);
        const stars = getStars(pct);

        saveScore(currentLesson.id, quizScore, total);

        let emoji, titleFr, titleAr;
        if (pct >= 90) {
            emoji = "🏆";
            titleFr = "Excellent !";
            titleAr = "!ممتاز";
        } else if (pct >= 60) {
            emoji = "👏";
            titleFr = "Très bien !";
            titleAr = "!جيّد جدّا";
        } else if (pct >= 30) {
            emoji = "💪";
            titleFr = "Continue !";
            titleAr = "!واصل المحاولة";
        } else {
            emoji = "📚";
            titleFr = "Révise encore !";
            titleAr = "!راجع الدرس مرّة أخرى";
        }

        resultsEmoji.textContent = emoji;
        resultsTitle.textContent = titleFr;
        resultsSubtitle.textContent = titleAr;
        resultsScore.textContent = `${quizScore} / ${total}`;
        resultsStars.textContent = stars || "—";

        showMode(resultsMode);
    }

    // ========== Event Listeners ==========
    btnBack.addEventListener("click", () => {
        showScreen(homeScreen);
        renderHome(); // Refresh stars
    });

    btnPrev.addEventListener("click", () => {
        if (currentWordIndex > 0) {
            currentWordIndex--;
            renderWord();
        }
    });

    btnNext.addEventListener("click", () => {
        if (currentWordIndex < currentLesson.words.length - 1) {
            currentWordIndex++;
            renderWord();
        }
    });

    btnSound.addEventListener("click", () => {
        const word = currentLesson.words[currentWordIndex];
        speakFrench(word.fr);
    });

    btnStartQuiz.addEventListener("click", startQuiz);

    btnNextQuestion.addEventListener("click", () => {
        currentQuizIndex++;
        renderQuizQuestion();
    });

    btnRetry.addEventListener("click", startQuiz);

    btnHomeResults.addEventListener("click", () => {
        showScreen(homeScreen);
        renderHome();
    });

    // Keyboard navigation
    document.addEventListener("keydown", (e) => {
        if (!lessonScreen.classList.contains("active")) return;

        if (vocabMode.classList.contains("active")) {
            if (e.key === "ArrowRight" && !btnNext.disabled) {
                currentWordIndex++;
                renderWord();
            } else if (e.key === "ArrowLeft" && !btnPrev.disabled) {
                currentWordIndex--;
                renderWord();
            } else if (e.key === " ") {
                e.preventDefault();
                speakFrench(currentLesson.words[currentWordIndex].fr);
            }
        }
    });

    // Touch swipe support for vocab cards
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener(
        "touchstart",
        (e) => {
            touchStartX = e.changedTouches[0].screenX;
        },
        { passive: true }
    );

    document.addEventListener(
        "touchend",
        (e) => {
            if (!vocabMode.classList.contains("active")) return;
            touchEndX = e.changedTouches[0].screenX;
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0 && !btnNext.disabled) {
                    currentWordIndex++;
                    renderWord();
                } else if (diff < 0 && !btnPrev.disabled) {
                    currentWordIndex--;
                    renderWord();
                }
            }
        },
        { passive: true }
    );

    // ========== Init ==========
    renderHome();
})();
