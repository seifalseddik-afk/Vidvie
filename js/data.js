/**
 * Lesson Data - French Learning App
 * 1st Year Primary School - Tunisia
 * Each word includes: French, phonetic (Arabic script), Arabic translation, emoji
 */

const LESSONS = [
    {
        id: 1,
        titleFr: "Les Salutations",
        titleAr: "التحيّات",
        emoji: "👋",
        color: "#4A90D9",
        words: [
            { fr: "Bonjour", phonetic: "بونجور", ar: "صباح الخير", emoji: "🌞" },
            { fr: "Bonsoir", phonetic: "بونسوار", ar: "مساء الخير", emoji: "🌙" },
            { fr: "Salut", phonetic: "سالو", ar: "مرحبا", emoji: "🙋" },
            { fr: "Au revoir", phonetic: "أو روفوار", ar: "إلى اللقاء", emoji: "👋" },
            { fr: "Merci", phonetic: "مارسي", ar: "شكرا", emoji: "🙏" },
            { fr: "S'il vous plaît", phonetic: "سيل فو بلي", ar: "من فضلك", emoji: "🤲" },
            { fr: "Oui", phonetic: "وي", ar: "نعم", emoji: "✅" },
            { fr: "Non", phonetic: "نون", ar: "لا", emoji: "❌" }
        ],
        quizType: "fr-to-ar"
    },
    {
        id: 2,
        titleFr: "Les Nombres (1-10)",
        titleAr: "الأعداد",
        emoji: "🔢",
        color: "#FF6B6B",
        words: [
            { fr: "Un", phonetic: "أن", ar: "واحد (١)", emoji: "1️⃣" },
            { fr: "Deux", phonetic: "دو", ar: "اثنان (٢)", emoji: "2️⃣" },
            { fr: "Trois", phonetic: "تروا", ar: "ثلاثة (٣)", emoji: "3️⃣" },
            { fr: "Quatre", phonetic: "كاتر", ar: "أربعة (٤)", emoji: "4️⃣" },
            { fr: "Cinq", phonetic: "سانك", ar: "خمسة (٥)", emoji: "5️⃣" },
            { fr: "Six", phonetic: "سيس", ar: "ستّة (٦)", emoji: "6️⃣" },
            { fr: "Sept", phonetic: "سات", ar: "سبعة (٧)", emoji: "7️⃣" },
            { fr: "Huit", phonetic: "ويت", ar: "ثمانية (٨)", emoji: "8️⃣" },
            { fr: "Neuf", phonetic: "نوف", ar: "تسعة (٩)", emoji: "9️⃣" },
            { fr: "Dix", phonetic: "ديس", ar: "عشرة (١٠)", emoji: "🔟" }
        ],
        quizType: "fr-to-ar"
    },
    {
        id: 3,
        titleFr: "Les Couleurs",
        titleAr: "الألوان",
        emoji: "🎨",
        color: "#6BCB77",
        words: [
            { fr: "Rouge", phonetic: "روج", ar: "أحمر", emoji: "🔴" },
            { fr: "Bleu", phonetic: "بلو", ar: "أزرق", emoji: "🔵" },
            { fr: "Vert", phonetic: "فار", ar: "أخضر", emoji: "🟢" },
            { fr: "Jaune", phonetic: "جون", ar: "أصفر", emoji: "🟡" },
            { fr: "Blanc", phonetic: "بلون", ar: "أبيض", emoji: "⚪" },
            { fr: "Noir", phonetic: "نوار", ar: "أسود", emoji: "⚫" },
            { fr: "Orange", phonetic: "أورونج", ar: "برتقالي", emoji: "🟠" },
            { fr: "Rose", phonetic: "روز", ar: "وردي", emoji: "🩷" }
        ],
        quizType: "emoji-to-fr"
    },
    {
        id: 4,
        titleFr: "Les Animaux",
        titleAr: "الحيوانات",
        emoji: "🐾",
        color: "#9B59B6",
        words: [
            { fr: "Chat", phonetic: "شا", ar: "قطّ", emoji: "🐱" },
            { fr: "Chien", phonetic: "شيان", ar: "كلب", emoji: "🐶" },
            { fr: "Oiseau", phonetic: "وازو", ar: "عصفور", emoji: "🐦" },
            { fr: "Poisson", phonetic: "بواسون", ar: "سمكة", emoji: "🐟" },
            { fr: "Lapin", phonetic: "لابان", ar: "أرنب", emoji: "🐰" },
            { fr: "Vache", phonetic: "فاش", ar: "بقرة", emoji: "🐄" },
            { fr: "Cheval", phonetic: "شوفال", ar: "حصان", emoji: "🐴" },
            { fr: "Mouton", phonetic: "موتون", ar: "خروف", emoji: "🐑" }
        ],
        quizType: "emoji-to-fr"
    },
    {
        id: 5,
        titleFr: "La Famille",
        titleAr: "العائلة",
        emoji: "👨‍👩‍👧‍👦",
        color: "#F39C12",
        words: [
            { fr: "Papa", phonetic: "بابا", ar: "أبي", emoji: "👨" },
            { fr: "Maman", phonetic: "مامان", ar: "أمّي", emoji: "👩" },
            { fr: "Frère", phonetic: "فرار", ar: "أخ", emoji: "👦" },
            { fr: "Sœur", phonetic: "سور", ar: "أخت", emoji: "👧" },
            { fr: "Grand-père", phonetic: "غرون بار", ar: "جدّ", emoji: "👴" },
            { fr: "Grand-mère", phonetic: "غرون مار", ar: "جدّة", emoji: "👵" },
            { fr: "Bébé", phonetic: "بيبي", ar: "رضيع", emoji: "👶" },
            { fr: "Famille", phonetic: "فامي", ar: "عائلة", emoji: "👨‍👩‍👧‍👦" }
        ],
        quizType: "fr-to-ar"
    },
    {
        id: 6,
        titleFr: "L'École",
        titleAr: "المدرسة",
        emoji: "🏫",
        color: "#E91E63",
        words: [
            { fr: "École", phonetic: "إيكول", ar: "مدرسة", emoji: "🏫" },
            { fr: "Livre", phonetic: "ليفر", ar: "كتاب", emoji: "📖" },
            { fr: "Cahier", phonetic: "كاييه", ar: "كرّاس", emoji: "📓" },
            { fr: "Stylo", phonetic: "ستيلو", ar: "قلم", emoji: "🖊️" },
            { fr: "Crayon", phonetic: "كرايون", ar: "قلم رصاص", emoji: "✏️" },
            { fr: "Table", phonetic: "طابل", ar: "طاولة", emoji: "🪑" },
            { fr: "Tableau", phonetic: "طابلو", ar: "سبّورة", emoji: "📋" },
            { fr: "Maître", phonetic: "ماتر", ar: "معلّم", emoji: "👨‍🏫" }
        ],
        quizType: "fr-to-ar"
    },
    {
        id: 7,
        titleFr: "Le Corps",
        titleAr: "جسم الإنسان",
        emoji: "🧍",
        color: "#4A90D9",
        words: [
            { fr: "Tête", phonetic: "تات", ar: "رأس", emoji: "🗣️" },
            { fr: "Yeux", phonetic: "يو", ar: "عيون", emoji: "👀" },
            { fr: "Nez", phonetic: "ني", ar: "أنف", emoji: "👃" },
            { fr: "Bouche", phonetic: "بوش", ar: "فم", emoji: "👄" },
            { fr: "Main", phonetic: "مان", ar: "يد", emoji: "✋" },
            { fr: "Pied", phonetic: "بيي", ar: "قدم", emoji: "🦶" },
            { fr: "Oreille", phonetic: "أوراي", ar: "أذن", emoji: "👂" },
            { fr: "Dent", phonetic: "دون", ar: "سنّ", emoji: "🦷" }
        ],
        quizType: "emoji-to-fr"
    },
    {
        id: 8,
        titleFr: "Les Fruits",
        titleAr: "الفواكه",
        emoji: "🍎",
        color: "#FFD93D",
        words: [
            { fr: "Pomme", phonetic: "بوم", ar: "تفّاحة", emoji: "🍎" },
            { fr: "Banane", phonetic: "بانان", ar: "موزة", emoji: "🍌" },
            { fr: "Orange", phonetic: "أورونج", ar: "برتقالة", emoji: "🍊" },
            { fr: "Fraise", phonetic: "فراز", ar: "فراولة", emoji: "🍓" },
            { fr: "Raisin", phonetic: "رازان", ar: "عنب", emoji: "🍇" },
            { fr: "Pastèque", phonetic: "باستاك", ar: "دلّاع", emoji: "🍉" },
            { fr: "Citron", phonetic: "سيترون", ar: "حامض", emoji: "🍋" },
            { fr: "Poire", phonetic: "بوار", ar: "إجّاص", emoji: "🍐" }
        ],
        quizType: "emoji-to-fr"
    }
];
