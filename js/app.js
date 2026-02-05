// ===== Arabic Learning App - Main Application Logic =====

// ===== State Management =====
const AppState = {
    currentPage: 'home',
    selectedLevel: null,
    currentQuizCategory: null,
    currentQuizQuestions: [],
    currentQuestionIndex: 0,
    quizScore: 0,
    quizCorrect: 0,
    quizWrong: 0,
    quizTimer: null,
    quizTimeLeft: 30,
    progress: {
        totalPoints: 0,
        completedLessons: [],
        completedQuizzes: 0,
        streakDays: 0,
        lastActiveDate: null,
        chatMessages: 0,
        perfectQuiz: false,
        categoriesVisited: [],
        activities: [],
        unlockedAchievements: []
    }
};

// ===== Initialize App =====
function initApp() {
    loadProgress();
    updateStreak();
    renderLessons();
    renderQuizCategories();
    renderAchievements();
    renderProgress();
    renderActivities();
}

// ===== Navigation =====
function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');

    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });

    AppState.currentPage = page;
    closeMobileMenu();
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (page === 'progress') {
        renderProgress();
        renderActivities();
        renderAchievements();
    }
}

function toggleMenu() {
    document.getElementById('mobileMenu').classList.toggle('show');
}

function closeMobileMenu() {
    document.getElementById('mobileMenu').classList.remove('show');
}

// ===== Level Selection =====
function selectLevel(level) {
    AppState.selectedLevel = level;
    document.querySelectorAll('.level-card').forEach(card => card.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
    navigateTo('lessons');
}

// ===== Lessons =====
function renderLessons(filter) {
    const grid = document.getElementById('lessonsGrid');
    if (!grid) return;

    let lessons = LESSONS_DATA;
    if (filter && filter !== 'all') {
        lessons = lessons.filter(l => l.category === filter);
    }

    grid.innerHTML = lessons.map(lesson => {
        const isCompleted = AppState.progress.completedLessons.includes(lesson.id);
        return `
            <div class="lesson-card" onclick="openLesson('${lesson.id}')">
                <div class="lesson-card-header ${lesson.category}">
                    <span class="lesson-category-tag">${lesson.categoryLabel}</span>
                    <h3>${isCompleted ? '&#9989; ' : ''}${lesson.title}</h3>
                </div>
                <div class="lesson-card-body">
                    <p>${lesson.description}</p>
                    <div class="lesson-meta">
                        <span>${lesson.points} نقطة</span>
                        <span class="difficulty ${lesson.difficulty}">${lesson.difficultyLabel}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function filterLessons(category) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    renderLessons(category);
}

function openLesson(lessonId) {
    const lesson = LESSONS_DATA.find(l => l.id === lessonId);
    if (!lesson) return;

    document.getElementById('lessonsGrid').style.display = 'none';
    document.querySelector('.category-tabs').style.display = 'none';
    document.getElementById('lessonDetail').style.display = 'block';

    let html = `<h2>${lesson.title}</h2>`;

    lesson.content.sections.forEach(section => {
        if (section.type === 'example') {
            html += `
                <div class="example-box">
                    <div class="example-label">${section.label}</div>
                    <p>${section.text.replace(/\n/g, '<br>')}</p>
                </div>
            `;
        } else if (section.type === 'tip') {
            html += `
                <div class="tip-box">
                    <div class="tip-label">&#128161; ${section.label}</div>
                    <p>${section.text.replace(/\n/g, '<br>')}</p>
                </div>
            `;
        } else {
            if (section.title) {
                html += `<h3>${section.title}</h3>`;
            }
            html += `<p>${section.text}</p>`;
        }
    });

    if (lesson.content.flashcards && lesson.content.flashcards.length > 0) {
        html += `<h3>&#127183; بطاقات تعليمية (اضغط لقلب البطاقة)</h3>`;
        html += `<div class="flashcard-grid">`;
        lesson.content.flashcards.forEach((card, index) => {
            html += `
                <div class="flashcard" onclick="flipCard(this)">
                    <div class="word">${card.word}</div>
                    <div class="meaning">${card.meaning}</div>
                </div>
            `;
        });
        html += `</div>`;
    }

    html += `
        <div class="lesson-actions">
            <button class="btn btn-primary btn-lg" onclick="completeLesson('${lesson.id}', ${lesson.points})">
                &#9989; أتممت الدرس
            </button>
        </div>
    `;

    document.getElementById('lessonContent').innerHTML = html;

    if (!AppState.progress.categoriesVisited.includes(lesson.category)) {
        AppState.progress.categoriesVisited.push(lesson.category);
        saveProgress();
    }
}

function closeLessonDetail() {
    document.getElementById('lessonsGrid').style.display = '';
    document.querySelector('.category-tabs').style.display = '';
    document.getElementById('lessonDetail').style.display = 'none';
}

function flipCard(element) {
    element.classList.toggle('flipped');
}

function completeLesson(lessonId, points) {
    if (!AppState.progress.completedLessons.includes(lessonId)) {
        AppState.progress.completedLessons.push(lessonId);
        AppState.progress.totalPoints += points;
        addActivity('lesson', `أكملت درس: ${LESSONS_DATA.find(l => l.id === lessonId).title}`, points);
        saveProgress();
        checkAchievements();
    }
    closeLessonDetail();
    renderLessons();

    showNotification('أحسنت! لقد أكملت الدرس بنجاح', 'success');
}

// ===== Quiz =====
function renderQuizCategories() {
    const container = document.getElementById('quizCategories');
    if (!container) return;

    container.innerHTML = Object.entries(QUIZ_DATA).map(([key, quiz]) => `
        <div class="quiz-category-card" onclick="startQuiz('${key}')">
            <div class="quiz-category-icon">${quiz.icon}</div>
            <h3>${quiz.title}</h3>
            <p>${quiz.description}</p>
            <div class="quiz-count">${quiz.questions.length} أسئلة</div>
        </div>
    `).join('');
}

function startQuiz(category) {
    AppState.currentQuizCategory = category;
    AppState.currentQuizQuestions = shuffleArray([...QUIZ_DATA[category].questions]);
    AppState.currentQuestionIndex = 0;
    AppState.quizScore = 0;
    AppState.quizCorrect = 0;
    AppState.quizWrong = 0;

    document.getElementById('quizSelection').style.display = 'none';
    document.getElementById('quizResults').style.display = 'none';
    document.getElementById('activeQuiz').style.display = 'block';

    document.getElementById('quizTotalQuestions').textContent = toArabicNum(AppState.currentQuizQuestions.length);

    showQuestion();
}

function showQuestion() {
    const question = AppState.currentQuizQuestions[AppState.currentQuestionIndex];
    const total = AppState.currentQuizQuestions.length;

    document.getElementById('quizQuestionNum').textContent = toArabicNum(AppState.currentQuestionIndex + 1);
    document.getElementById('quizScore').textContent = AppState.quizScore;
    document.getElementById('quizProgressBar').style.width = ((AppState.currentQuestionIndex) / total * 100) + '%';

    AppState.quizTimeLeft = 30;
    updateTimerDisplay();
    clearInterval(AppState.quizTimer);
    AppState.quizTimer = setInterval(() => {
        AppState.quizTimeLeft--;
        updateTimerDisplay();
        if (AppState.quizTimeLeft <= 0) {
            clearInterval(AppState.quizTimer);
            handleAnswer(-1);
        }
    }, 1000);

    document.getElementById('quizBody').innerHTML = `
        <div class="quiz-question">${question.question}</div>
        <div class="quiz-options">
            ${question.options.map((opt, i) => `
                <button class="quiz-option" onclick="handleAnswer(${i})">${opt}</button>
            `).join('')}
        </div>
        <div class="quiz-explanation" id="quizExplanation">
            <strong>&#128161; التوضيح:</strong> ${question.explanation}
        </div>
        <button class="btn btn-primary quiz-next-btn" id="quizNextBtn" onclick="nextQuestion()">
            ${AppState.currentQuestionIndex < total - 1 ? 'السؤال التالي &#8592;' : 'عرض النتائج'}
        </button>
    `;
}

function handleAnswer(selectedIndex) {
    clearInterval(AppState.quizTimer);
    const question = AppState.currentQuizQuestions[AppState.currentQuestionIndex];
    const options = document.querySelectorAll('.quiz-option');

    options.forEach(opt => opt.classList.add('disabled'));

    if (selectedIndex === question.correct) {
        options[selectedIndex].classList.add('correct');
        AppState.quizScore += 10;
        AppState.quizCorrect++;
    } else {
        if (selectedIndex >= 0) {
            options[selectedIndex].classList.add('wrong');
        }
        options[question.correct].classList.add('correct');
        AppState.quizWrong++;
    }

    document.getElementById('quizExplanation').classList.add('show');
    document.getElementById('quizNextBtn').classList.add('show');
    document.getElementById('quizScore').textContent = AppState.quizScore;
}

function nextQuestion() {
    AppState.currentQuestionIndex++;
    if (AppState.currentQuestionIndex < AppState.currentQuizQuestions.length) {
        showQuestion();
    } else {
        showResults();
    }
}

function showResults() {
    clearInterval(AppState.quizTimer);
    document.getElementById('activeQuiz').style.display = 'none';
    document.getElementById('quizResults').style.display = 'block';

    const total = AppState.currentQuizQuestions.length;
    const percentage = Math.round((AppState.quizCorrect / total) * 100);

    document.getElementById('resultScore').textContent = AppState.quizScore;
    document.getElementById('resultCorrect').textContent = AppState.quizCorrect;
    document.getElementById('resultWrong').textContent = AppState.quizWrong;
    document.getElementById('resultPercentage').textContent = percentage + '%';

    if (percentage >= 90) {
        document.getElementById('resultsIcon').textContent = '🏆';
        document.getElementById('resultsTitle').textContent = 'ممتاز! أداء رائع!';
    } else if (percentage >= 70) {
        document.getElementById('resultsIcon').textContent = '🌟';
        document.getElementById('resultsTitle').textContent = 'جيد جداً! استمر!';
    } else if (percentage >= 50) {
        document.getElementById('resultsIcon').textContent = '👍';
        document.getElementById('resultsTitle').textContent = 'جيد! يمكنك التحسن أكثر';
    } else {
        document.getElementById('resultsIcon').textContent = '💪';
        document.getElementById('resultsTitle').textContent = 'حاول مرة أخرى!';
    }

    if (percentage === 100) {
        AppState.progress.perfectQuiz = true;
    }

    AppState.progress.totalPoints += AppState.quizScore;
    AppState.progress.completedQuizzes++;
    addActivity('quiz', `أكملت اختبار: ${QUIZ_DATA[AppState.currentQuizCategory].title} (${percentage}%)`, AppState.quizScore);
    saveProgress();
    checkAchievements();
}

function retryQuiz() {
    startQuiz(AppState.currentQuizCategory);
}

function showQuizSelection() {
    document.getElementById('activeQuiz').style.display = 'none';
    document.getElementById('quizResults').style.display = 'none';
    document.getElementById('quizSelection').style.display = 'block';
    clearInterval(AppState.quizTimer);
}

function updateTimerDisplay() {
    const seconds = AppState.quizTimeLeft;
    const display = `00:${seconds.toString().padStart(2, '0')}`;
    document.getElementById('timerDisplay').textContent = display;

    const timerEl = document.getElementById('quizTimer');
    if (seconds <= 10) {
        timerEl.style.color = 'var(--danger)';
    } else {
        timerEl.style.color = 'var(--text)';
    }
}

// ===== Progress =====
function renderProgress() {
    const p = AppState.progress;
    const el = (id) => document.getElementById(id);

    if (el('streakDays')) el('streakDays').textContent = p.streakDays;
    if (el('totalPoints')) el('totalPoints').textContent = p.totalPoints;
    if (el('completedLessons')) el('completedLessons').textContent = p.completedLessons.length;
    if (el('completedQuizzes')) el('completedQuizzes').textContent = p.completedQuizzes;
}

function renderAchievements() {
    const grid = document.getElementById('achievementsGrid');
    if (!grid) return;

    grid.innerHTML = ACHIEVEMENTS_DATA.map(achievement => {
        const isUnlocked = AppState.progress.unlockedAchievements.includes(achievement.id);
        return `
            <div class="achievement-card ${isUnlocked ? 'unlocked' : 'locked'}">
                <div class="achievement-icon">${achievement.icon}</div>
                <h4>${achievement.title}</h4>
                <p>${achievement.description}</p>
            </div>
        `;
    }).join('');
}

function renderActivities() {
    const list = document.getElementById('activityList');
    if (!list) return;

    const activities = AppState.progress.activities;

    if (activities.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">&#128203;</span>
                <p>لم تبدأ أي نشاط بعد. ابدأ التعلم الآن!</p>
                <button class="btn btn-primary" onclick="navigateTo('lessons')">ابدأ التعلم</button>
            </div>
        `;
        return;
    }

    list.innerHTML = activities.slice(0, 10).map(activity => `
        <div class="activity-item">
            <div class="activity-icon">${activity.type === 'lesson' ? '📖' : activity.type === 'quiz' ? '✅' : activity.type === 'achievement' ? '🏆' : '💬'}</div>
            <div class="activity-info">
                <strong>${activity.text}</strong>
                <span>${formatDate(activity.date)}</span>
            </div>
            <div class="activity-points">+${activity.points}</div>
        </div>
    `).join('');
}

function addActivity(type, text, points) {
    AppState.progress.activities.unshift({
        type,
        text,
        points,
        date: new Date().toISOString()
    });

    if (AppState.progress.activities.length > 50) {
        AppState.progress.activities = AppState.progress.activities.slice(0, 50);
    }
}

function checkAchievements() {
    const p = AppState.progress;

    ACHIEVEMENTS_DATA.forEach(achievement => {
        if (p.unlockedAchievements.includes(achievement.id)) return;

        let unlocked = false;
        switch (achievement.id) {
            case 'first-lesson': unlocked = p.completedLessons.length >= 1; break;
            case 'five-lessons': unlocked = p.completedLessons.length >= 5; break;
            case 'first-quiz': unlocked = p.completedQuizzes >= 1; break;
            case 'perfect-quiz': unlocked = p.perfectQuiz; break;
            case 'points-100': unlocked = p.totalPoints >= 100; break;
            case 'points-500': unlocked = p.totalPoints >= 500; break;
            case 'streak-3': unlocked = p.streakDays >= 3; break;
            case 'streak-7': unlocked = p.streakDays >= 7; break;
            case 'all-categories': unlocked = p.categoriesVisited.length >= 5; break;
            case 'chat-5': unlocked = p.chatMessages >= 5; break;
        }

        if (unlocked) {
            p.unlockedAchievements.push(achievement.id);
            addActivity('achievement', `إنجاز جديد: ${achievement.title}`, 25);
            p.totalPoints += 25;
            showNotification(`&#127942; إنجاز جديد: ${achievement.title}!`, 'achievement');
        }
    });

    saveProgress();
}

// ===== Streak =====
function updateStreak() {
    const today = new Date().toDateString();
    const lastActive = AppState.progress.lastActiveDate;

    if (lastActive === today) return;

    if (lastActive) {
        const lastDate = new Date(lastActive);
        const diff = Math.floor((new Date(today) - lastDate) / (1000 * 60 * 60 * 24));

        if (diff === 1) {
            AppState.progress.streakDays++;
        } else if (diff > 1) {
            AppState.progress.streakDays = 1;
        }
    } else {
        AppState.progress.streakDays = 1;
    }

    AppState.progress.lastActiveDate = today;
    saveProgress();
}

// ===== Persistence =====
function saveProgress() {
    try {
        localStorage.setItem('arabicApp_progress', JSON.stringify(AppState.progress));
    } catch (e) {
        // Silently fail if localStorage is not available
    }
}

function loadProgress() {
    try {
        const saved = localStorage.getItem('arabicApp_progress');
        if (saved) {
            const parsed = JSON.parse(saved);
            AppState.progress = { ...AppState.progress, ...parsed };
        }
    } catch (e) {
        // Use default progress
    }
}

// ===== Utilities =====
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function toArabicNum(num) {
    const arabicNums = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    return String(num).replace(/[0-9]/g, d => arabicNums[d]);
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'الآن';
    if (diff < 3600) return `منذ ${Math.floor(diff / 60)} دقيقة`;
    if (diff < 86400) return `منذ ${Math.floor(diff / 3600)} ساعة`;
    if (diff < 604800) return `منذ ${Math.floor(diff / 86400)} يوم`;
    return date.toLocaleDateString('ar-SA');
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        padding: 16px 32px;
        border-radius: 12px;
        font-family: 'Cairo', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ${type === 'success' ? 'background: #0d904f; color: white;' :
          type === 'achievement' ? 'background: linear-gradient(135deg, #f9a825, #f57f17); color: white;' :
          'background: #1a73e8; color: white;'}
    `;
    notification.innerHTML = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===== Initialize on DOM Ready =====
document.addEventListener('DOMContentLoaded', initApp);
