let studentName = ''; // Assuming you get it from local storage
let questions = [];

let score = 0;
let explanationEnabled = false; // Initially disabled

// Get query parameters
const urlParams = new URLSearchParams(window.location.search);
const fileLoc = urlParams.get('file');
const examFile = urlParams.get('exam');
let questionsFile;
let answersFile;
let explanationFile; // Add explanation file variable

if (examFile) {
    questionsFile = fileLoc + `_question.txt`;
    answersFile = fileLoc + `_ans_key.txt`;
    explanationFile = fileLoc + `_explanation.txt`; //added
} else {
    questionsFile = fileLoc + `/question.txt`;
    answersFile = fileLoc + `/answer.txt`;
    explanationFile = fileLoc + `/explanation.txt`; //added
}

let subjectName = urlParams.get('subject');
const shuffleQuestions = urlParams.get('shuffle') === 'true';

if (subjectName) {
    subjectName = subjectName;
}

let headName = document.getElementById('headname');
headName.textContent = subjectName;

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function loadQuestionsAndAnswers() {
    Promise.all([
        fetch(questionsFile).then(response => response.text()),
        fetch(answersFile).then(response => response.json()),
        fetch(explanationFile).then(response => response.json()) // Load explanations
    ]).then(([questionsText, answersJson, explanationJson]) => { // added explanationJson
        const lines = questionsText.split('\n').filter(line => line.trim() !== '');
        let questionList = [];
        let currentQuestion = {};

        lines.forEach(line => {
            if (line.match(/^\d+\./)) {
                if (currentQuestion.question) {
                    questionList.push(currentQuestion);
                }
                currentQuestion = {
                    question: line.replace(/^\d+\.\s*/, ""),
                    options: []
                };
            } else if (line.match(/^[A-D]\)/)) {
                const optionText = line.replace(/^[A-D]\)\s*/, "");
                currentQuestion.options.push(optionText);
            }
        });

        if (currentQuestion.question) {
            questionList.push(currentQuestion);
        }

        questions = questionList.map((q, index) => {
            const correctAnswers = answersJson[index + 1];
            const correctAnswerArray = Array.isArray(correctAnswers) ? correctAnswers : [correctAnswers];
            let optionsWithIndex = q.options.map((opt, i) => ({ opt, originalIndex: i }));

            if (shuffleQuestions) {
                shuffleArray(optionsWithIndex);
            }

            const shuffledOptions = optionsWithIndex.map(optObj => optObj.opt);
            const correctIndices = correctAnswerArray.map(correctAnswer => {
                const originalIndex = correctAnswer.charCodeAt(0) - 'A'.charCodeAt(0);
                return optionsWithIndex.findIndex(optObj => optObj.originalIndex === originalIndex);
            });

            const questionObject = {
                question: q.question,
                options: shuffledOptions,
                correctAnswerIndices: correctIndices
            };

            // Add explanation if it exists
            if (explanationJson && explanationJson[index + 1]) {
                questionObject.explanation = explanationJson[index + 1];
            }

            return questionObject;
        });

        if (shuffleQuestions) {
            shuffleArray(questions);
        }

        displayQuestions();
    }).catch(error => {
        console.error("Error loading questions or answers:", error);
    });
}

function handleOptionChange(questionIndex, selectedOptionIndex, selectedRadio) {
    const floatingCircle = document.getElementById('floating-circle');
    floatingCircle.style.display = 'flex';
    const correctOptionIndices = questions[questionIndex].correctAnswerIndices;
    const selectedOptionLabel = selectedRadio.parentElement;

    // Check if selected option is among the correct answers
    const isCorrect = correctOptionIndices.includes(selectedOptionIndex);

    const correctOptions = Array.from(document.querySelectorAll(`input[name="question-${questionIndex}"]`))
        .filter((_, index) => correctOptionIndices.includes(index));
    const correctOptionLabels = correctOptions.map(option => option.parentElement);

    // Disable all radio buttons for this question after selection
    document.querySelectorAll(`input[name="question-${questionIndex}"]`).forEach(radio => {
        radio.disabled = true;
    });

    if (isCorrect) {
        showNotification('Correct', 'correct');
        selectedOptionLabel.style.backgroundColor = '#5db160'; // Light green
        correctOptionLabels.forEach(label => label.style.backgroundColor = '#5db160'); // Highlight all correct options
        score++;
    } else {
        showNotification('Incorrect', 'incorrect');
        selectedOptionLabel.style.backgroundColor = '#f4a5a5'; // Light red
        correctOptionLabels.forEach(label => label.style.backgroundColor = '#5db160'); // Highlight all correct options

        if (explanationEnabled && questions[questionIndex].explanation) { // Check if explanation exists
            const explanationDiv = document.createElement('div');
            explanationDiv.classList.add('explanation');
            explanationDiv.innerHTML = questions[questionIndex].explanation;


            // Add explanation under correct options
            const correctOptionIndices = questions[questionIndex].correctAnswerIndices;
            const correctOptionRadios = Array.from(document.querySelectorAll(`input[name="question-${questionIndex}"]`))
                .filter((_, index) => correctOptionIndices.includes(index));

            correctOptionRadios.forEach(radio => {
                const optionLabel = radio.parentElement;
                optionLabel.parentElement.appendChild(explanationDiv); // Add to the <li> element
            })

            explanationDiv.style.display = 'block';
        }
    }

    updateUI();
}

function displayQuestions() {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    questions.forEach((q, index) => {
        const questionBox = document.createElement('div');
        questionBox.classList.add('question-box');

        const questionNumber = document.createElement('div');
        questionNumber.classList.add('question-number');
        questionNumber.textContent = `Question ${index + 1}`;

        const questionText = document.createElement('div');
        questionText.classList.add('question');
        questionText.innerHTML = q.question; // Use innerHTML to render HTML tags in the question text

        const optionsList = document.createElement('ul');
        optionsList.classList.add('options');

        q.options.forEach((opt, optIndex) => {
            const optionItem = document.createElement('li');
            const label = document.createElement('label');
            const radio = document.createElement('input');

            radio.type = 'radio';
            radio.name = `question-${index}`;
            radio.value = String.fromCharCode(65 + optIndex); // A, B, C, D serially
            radio.addEventListener('change', () => handleOptionChange(index, optIndex, radio));

            label.classList.add('option-label');
            label.appendChild(radio);

            const optionLabel = document.createElement('span');
            optionLabel.textContent = `${String.fromCharCode(65 + optIndex)}) `;
            optionLabel.style.display = 'inline-block';
            optionLabel.style.marginRight = '5px'; // Adjust spacing

            const optionContent = document.createElement('span');
            optionContent.innerHTML = opt;

            label.style.display = 'flex';
            label.style.alignItems = 'flex-start'; // Aligns content to the top
            label.style.flexWrap = 'wrap'; // Ensures text and images wrap properly

            label.appendChild(optionLabel);
            label.appendChild(optionContent);

            optionItem.appendChild(label);
            optionsList.appendChild(optionItem);
        });

        questionBox.appendChild(questionNumber);
        questionBox.appendChild(questionText);
        questionBox.appendChild(optionsList);
        container.appendChild(questionBox);
    });

    updateUI();
}

function updateUI() {
    document.getElementById('score-banner').textContent = `Score: ${score} / ${questions.length}`;
    const questionsLeft = questions.length - getAnsweredQuestionsCount();
    document.getElementById('questions-left').textContent = `Questions Left: ${questionsLeft}`;

    // Update the floating circle
    document.getElementById('floating-circle').textContent = `${score}`;

}

function getAnsweredQuestionsCount() {
    let count = 0;
    questions.forEach((_, index) => {
        const selectedOptions = document.querySelectorAll(`input[name="question-${index}"]:checked`);
        if (selectedOptions.length > 0) {
            count++;
        }
    });
    return count;
}

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = type;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 1000);
}

function showExamEndMessage() {
    const container = document.getElementById('questions-container');
    const message = document.createElement('div');
    message.classList.add('exam-end-message');
    message.textContent = `You have completed the test. Your final score is ${score} out of ${questions.length}.`;
    container.innerHTML = '';
    container.appendChild(message);
}

// Add event listener for explanation toggle
document.getElementById('explanationToggle').addEventListener('change', function () {
    explanationEnabled = this.checked;
});

function endExam() {
    const questionsAnswered = getAnsweredQuestionsCount();
    const accuracy = questions.length > 0 ? ((score / questions.length) * 100).toFixed(2) : 0;

    // Display the final score, student name, and accuracy
    const container = document.getElementById('questions-container');
    container.innerHTML = `
        <div class="exam-end-message">
            <h2>Exam Completed</h2>
            <p><strong>Student Name:</strong> ${studentName}</p>
            <p><strong>Final Score:</strong> ${score} / ${questions.length}</p>
            <p><strong>Accuracy:</strong> ${accuracy}%</p>
        </div>
    `;
}

// Load questions and answers on page load
loadQuestionsAndAnswers();
