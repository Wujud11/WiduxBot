import os
from models import db, Question
from questions_sample import get_sample_questions

def load_user_questions():
    """Load questions from the attached file or sample questions"""
    # First try to parse the provided questions file
    questions_data = []
    file_paths = ['attached_assets/Pasted--60-2-1-15-7-22-3-2--1743933381711.txt', 'questions.txt']
    file_found = False
    added_questions = 0
    
    for file_path in file_paths:
        if os.path.exists(file_path):
            file_found = True
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Found {len(lines)} lines in the file {file_path}.")
            
            # Skip header (first 4 lines) and process the rest if it's the pasted file
            i = 4 if file_path.startswith('attached_assets/Pasted') else 0
            
            while i < len(lines):
                try:
                    # The format in the file is different than expected
                    # It appears to be sequential numbers followed by question and answer
                    # Let's read until we get a question and an answer
                    current_line = lines[i].strip()
                    
                    # Skip empty lines
                    if not current_line:
                        i += 1
                        continue
                        
                    # Try to determine if this is a numeric sequence marker
                    if current_line.isdigit():
                        # We found a number, the next line might be a question
                        if i + 1 < len(lines):
                            question_text = lines[i + 1].strip()
                            
                            # And the next line might be an answer
                            if i + 2 < len(lines):
                                correct_answer = lines[i + 2].strip()
                                
                                # If both question and answer are non-empty, process them
                                if question_text and correct_answer:
                                    print(f"Processing question #{current_line}: {question_text}")
                                    
                                    # Clean up any quotation marks or extra spaces
                                    correct_answer = correct_answer.strip('"\'')
                                    
                                    # Handle multiple possible answers
                                    answers = []
                                    if "، " in correct_answer:
                                        answers = [ans.strip() for ans in correct_answer.split("، ")]
                                    elif "," in correct_answer:
                                        answers = [ans.strip() for ans in correct_answer.split(",")]
                                    else:
                                        answers = [correct_answer]
                                    
                                    if len(answers) > 1:
                                        main_answer = answers[0]
                                        alt_answers = ','.join(answers[1:])
                                    else:
                                        main_answer = correct_answer
                                        alt_answers = None
                                    
                                    # Determine category based on question content
                                    category = determine_category(question_text)
                                    
                                    # Check if question already exists
                                    existing = Question.query.filter_by(question=question_text).first()
                                    if existing:
                                        print(f"Question already exists: {question_text}")
                                        i += 3  # Skip this question's lines
                                        continue
                                    
                                    # Add the question to the database
                                    question = Question(
                                        question=question_text,
                                        correct_answer=main_answer,
                                        alternative_answers=alt_answers,
                                        category=category,
                                        difficulty='normal'
                                    )
                                    
                                    db.session.add(question)
                                    added_questions += 1
                                    questions_data.append((question_text, main_answer))
                                    
                                    # Skip to the next set of lines
                                    i += 3
                                else:
                                    # Skip this line if either question or answer is empty
                                    i += 1
                            else:
                                # Not enough lines left for a complete question
                                i += 1
                        else:
                            # Not enough lines left for a complete question
                            i += 1
                    else:
                        # Not a number, just skip this line
                        i += 1
                        
                except Exception as e:
                    print(f"Error processing question at line {i}: {e}")
                    i += 1  # Move to the next line
            
            break  # If we've processed one file, we're done
    
    # If no file found or no questions added, use sample questions
    if not file_found or added_questions == 0:
        print("No question file found or no questions added. Loading sample questions...")
        sample_questions = get_sample_questions()
        
        for q in sample_questions:
            # Check if question already exists
            existing = Question.query.filter_by(question=q['question']).first()
            if existing:
                print(f"Sample question already exists: {q['question']}")
                continue
            
            # Add the question to the database
            question = Question(
                question=q['question'],
                correct_answer=q['correct_answer'],
                alternative_answers=q['alternative_answers'],
                category=q['category'],
                difficulty=q['difficulty']
            )
            
            db.session.add(question)
            added_questions += 1
    
    # Commit all questions to the database
    db.session.commit()
    
    print(f"Successfully added {added_questions} questions to the database")
    return added_questions

def determine_category(question_text):
    """Simple category determination based on keywords in the question"""
    question_lower = question_text.lower()
    
    if any(keyword in question_lower for keyword in ['كرة', 'رياضة', 'لاعب', 'منتخب', 'نادي', 'فريق', 'كأس']):
        return 'رياضة'
    elif any(keyword in question_lower for keyword in ['عاصمة', 'دولة', 'قارة', 'جبل', 'نهر', 'بحر', 'محيط']):
        return 'جغرافيا'
    elif any(keyword in question_lower for keyword in ['عنصر', 'كيميائي', 'فيزياء', 'علوم', 'طب', 'عدد', 'كروموسوم']):
        return 'علوم'
    elif any(keyword in question_lower for keyword in ['قرآن', 'رسول', 'النبي', 'الله', 'الإسلام', 'دين']):
        return 'دين'
    elif any(keyword in question_lower for keyword in ['تاريخ', 'سنة', 'حرب', 'معركة', 'سقطت', 'أسست', 'عام']):
        return 'تاريخ'
    elif any(keyword in question_lower for keyword in ['رئيس', 'زعيم', 'حاكم', 'ملك', 'أمير', 'سياسة']):
        return 'سياسة'
    elif any(keyword in question_lower for keyword in ['موسيقى', 'لحن', 'أغنية', 'فن']):
        return 'فن وثقافة'
    elif any(keyword in question_lower for keyword in ['رياضيات', 'حساب', '+', '-', '*', '/']):
        return 'رياضيات'
    
    return 'عام'  # Default category