import os
import numpy as np
import pandas as pd

def generate_library_dataset(num_samples=600, random_seed=42):
    """
    Generates a realistic synthetic dataset for Library Book Demand Prediction.
    
    Features:
    - book_category: Subject category of the book
    - month: Month of the academic year (1-12)
    - semester: Academic semester (1-8)
    - number_of_students: Number of enrolled students in relevant courses
    - previous_borrowing_count: Number of times books in this category were borrowed in the prior month
    - previous_demand: Total calculated demand count from prior cycle
    - demand: Target feature - future total demand count
    """
    np.random.seed(random_seed)
    
    categories = [
        'Computer Science', 
        'Engineering', 
        'Mathematics', 
        'Physics', 
        'Business', 
        'Literature', 
        'History', 
        'Medical'
    ]
    
    category_weights = {
        'Computer Science': 1.35,
        'Engineering': 1.25,
        'Medical': 1.20,
        'Business': 1.10,
        'Mathematics': 1.05,
        'Physics': 0.95,
        'Literature': 0.85,
        'History': 0.75
    }

    book_category = np.random.choice(categories, size=num_samples)
    month = np.random.randint(1, 13, size=num_samples)
    semester = np.random.randint(1, 9, size=num_samples)
    number_of_students = np.random.randint(50, 501, size=num_samples)
    
    base_student_factor = number_of_students * 0.4
    previous_borrowing_count = np.clip(
        np.random.normal(loc=base_student_factor, scale=35, size=num_samples).astype(int), 
        a_min=10, 
        a_max=450
    )
    previous_demand = np.clip(
        previous_borrowing_count + np.random.normal(loc=15, scale=20, size=num_samples).astype(int), 
        a_min=15, 
        a_max=480
    )
    
    demands = []
    for i in range(num_samples):
        cat = book_category[i]
        m = month[i]
        students = number_of_students[i]
        prev_borrow = previous_borrowing_count[i]
        prev_demand = previous_demand[i]
        
        cat_mult = category_weights[cat]
        
        if m in [5, 12]:
            season_mult = 1.30  # Exam season peak
        elif m in [3, 4, 10, 11]:
            season_mult = 1.15  # Mid-term project season
        elif m in [6, 7]:
            season_mult = 0.65  # Summer break low
        else:
            season_mult = 1.00  # Normal semester months
            
        calculated_demand = (
            0.35 * prev_borrow +
            0.35 * prev_demand +
            0.20 * (students * 0.5) +
            np.random.normal(0, 15)
        ) * cat_mult * season_mult
        
        final_demand = int(max(15, round(calculated_demand)))
        demands.append(final_demand)
        
    df = pd.DataFrame({
        'book_category': book_category,
        'month': month,
        'semester': semester,
        'number_of_students': number_of_students,
        'previous_borrowing_count': previous_borrowing_count,
        'previous_demand': previous_demand,
        'demand': demands
    })
    
    return df

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "library_books_dataset.csv")
    df = generate_library_dataset(num_samples=600)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated sample dataset with {len(df)} rows at: {output_path}")
