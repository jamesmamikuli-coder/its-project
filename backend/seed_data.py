# ============================================================
#  seed_data.py  —  Populate the database with initial data
#
#  Run this AFTER starting the server for the first time to
#  add sample quiz questions and knowledge base articles.
#
#  HOW TO RUN:
#     python seed_data.py
# ============================================================

import sys
import os

# Add the backend folder to Python's path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.models import Question, KnowledgeArticle

app = create_app()

# ── Quiz Questions ──────────────────────────────────────
# Each question has: topic, subtopic, question text,
# 4 answer options, correct answer letter, explanation, difficulty (1/2/3)

QUESTIONS = [
    # ── DATA STRUCTURES ──
    {
        "topic": "Data Structures",
        "subtopic": "Arrays",
        "question_text": "What is the time complexity of accessing an element in an array by index?",
        "option_a": "O(n)",
        "option_b": "O(log n)",
        "option_c": "O(1)",
        "option_d": "O(n²)",
        "correct_answer": "C",
        "explanation": "Arrays store elements in contiguous memory locations. Since the memory address of any element can be calculated directly using its index (base_address + index × element_size), access is always O(1) — constant time.",
        "difficulty": 1
    },
    {
        "topic": "Data Structures",
        "subtopic": "Linked Lists",
        "question_text": "In a singly linked list, which operation has O(1) time complexity?",
        "option_a": "Searching for an element",
        "option_b": "Inserting at the beginning",
        "option_c": "Accessing the last element",
        "option_d": "Deleting the last element",
        "correct_answer": "B",
        "explanation": "Inserting at the beginning of a singly linked list is O(1) because we just create a new node, point it to the current head, and update the head pointer — no traversal needed.",
        "difficulty": 1
    },
    {
        "topic": "Data Structures",
        "subtopic": "Stacks",
        "question_text": "Which principle does a Stack data structure follow?",
        "option_a": "FIFO — First In First Out",
        "option_b": "FILO — First In Last Out",
        "option_c": "LIFO — Last In First Out",
        "option_d": "Random Access",
        "correct_answer": "C",
        "explanation": "A Stack is a LIFO (Last In First Out) structure. The last element pushed onto the stack is the first one to be popped off — like a stack of plates.",
        "difficulty": 1
    },
    {
        "topic": "Data Structures",
        "subtopic": "Queues",
        "question_text": "Which data structure is best suited for implementing a task scheduler (processes handled in order of arrival)?",
        "option_a": "Stack",
        "option_b": "Queue",
        "option_c": "Binary Tree",
        "option_d": "Hash Table",
        "correct_answer": "B",
        "explanation": "A Queue follows FIFO (First In First Out), making it ideal for task scheduling where the first task to arrive should be the first to be processed.",
        "difficulty": 1
    },
    {
        "topic": "Data Structures",
        "subtopic": "Trees",
        "question_text": "In a Binary Search Tree (BST), where are values smaller than the root stored?",
        "option_a": "In the right subtree",
        "option_b": "In the left subtree",
        "option_c": "At the root",
        "option_d": "In a separate list",
        "correct_answer": "B",
        "explanation": "BST property: all values in the left subtree are less than the root, and all values in the right subtree are greater. This ordering enables efficient O(log n) search.",
        "difficulty": 1
    },
    {
        "topic": "Data Structures",
        "subtopic": "Hash Tables",
        "question_text": "What is the average-case time complexity for inserting a key-value pair into a Hash Table?",
        "option_a": "O(n)",
        "option_b": "O(log n)",
        "option_c": "O(n log n)",
        "option_d": "O(1)",
        "correct_answer": "D",
        "explanation": "Hash tables use a hash function to compute the index directly. On average (with few collisions), insertion, deletion, and lookup are all O(1) constant time operations.",
        "difficulty": 2
    },
    {
        "topic": "Data Structures",
        "subtopic": "Graphs",
        "question_text": "Which graph traversal algorithm uses a Queue data structure internally?",
        "option_a": "Depth First Search (DFS)",
        "option_b": "Dijkstra's Algorithm",
        "option_c": "Breadth First Search (BFS)",
        "option_d": "Bellman-Ford",
        "correct_answer": "C",
        "explanation": "BFS explores nodes level by level (all neighbours before going deeper). It uses a Queue to track which node to visit next, ensuring FIFO order.",
        "difficulty": 2
    },

    # ── ALGORITHMS ──
    {
        "topic": "Algorithms",
        "subtopic": "Sorting",
        "question_text": "What is the best-case time complexity of Bubble Sort?",
        "option_a": "O(n²)",
        "option_b": "O(n log n)",
        "option_c": "O(n)",
        "option_d": "O(1)",
        "correct_answer": "C",
        "explanation": "In the best case (already sorted array), an optimised Bubble Sort makes one pass without any swaps and terminates early — resulting in O(n) time.",
        "difficulty": 2
    },
    {
        "topic": "Algorithms",
        "subtopic": "Sorting",
        "question_text": "Which sorting algorithm works by dividing the array into halves, sorting each half, then merging them?",
        "option_a": "Quick Sort",
        "option_b": "Heap Sort",
        "option_c": "Insertion Sort",
        "option_d": "Merge Sort",
        "correct_answer": "D",
        "explanation": "Merge Sort is a divide-and-conquer algorithm. It splits the array into halves recursively until single elements, then merges them in sorted order. Time complexity is O(n log n) in all cases.",
        "difficulty": 1
    },
    {
        "topic": "Algorithms",
        "subtopic": "Searching",
        "question_text": "Binary Search requires that the input array is:",
        "option_a": "Unsorted",
        "option_b": "Sorted",
        "option_c": "Stored in a linked list",
        "option_d": "Of even length",
        "correct_answer": "B",
        "explanation": "Binary Search works by comparing the target to the middle element and discarding half the array each time. This only works correctly if the array is sorted.",
        "difficulty": 1
    },
    {
        "topic": "Algorithms",
        "subtopic": "Complexity",
        "question_text": "What does 'Big O notation' measure in algorithm analysis?",
        "option_a": "The exact running time in seconds",
        "option_b": "The number of lines of code",
        "option_c": "The upper bound of an algorithm's growth rate",
        "option_d": "The memory address of variables",
        "correct_answer": "C",
        "explanation": "Big O notation describes the worst-case growth rate of an algorithm's time or space requirements as the input size (n) grows. It's an upper bound — not the exact time.",
        "difficulty": 2
    },

    # ── DATABASES ──
    {
        "topic": "Databases",
        "subtopic": "SQL Basics",
        "question_text": "Which SQL command is used to retrieve data from a table?",
        "option_a": "INSERT",
        "option_b": "UPDATE",
        "option_c": "SELECT",
        "option_d": "DELETE",
        "correct_answer": "C",
        "explanation": "SELECT is the SQL command for querying (reading) data. Example: SELECT * FROM students WHERE grade = 'A'; — retrieves all A-grade students.",
        "difficulty": 1
    },
    {
        "topic": "Databases",
        "subtopic": "Normalisation",
        "question_text": "What is the main goal of database normalisation?",
        "option_a": "To increase query response time",
        "option_b": "To reduce data redundancy and improve integrity",
        "option_c": "To add more tables to the database",
        "option_d": "To encrypt sensitive data",
        "correct_answer": "B",
        "explanation": "Normalisation organises a database to minimise redundancy (storing the same data in multiple places) and dependency. This prevents anomalies during INSERT, UPDATE, and DELETE operations.",
        "difficulty": 2
    },
    {
        "topic": "Databases",
        "subtopic": "Keys",
        "question_text": "A Foreign Key in a relational database is used to:",
        "option_a": "Uniquely identify each row in its own table",
        "option_b": "Encrypt data in the table",
        "option_c": "Establish a link between two tables",
        "option_d": "Speed up search queries",
        "correct_answer": "C",
        "explanation": "A Foreign Key is a column that references the Primary Key of another table, creating a relationship between them. This enforces referential integrity — you can't reference a row that doesn't exist.",
        "difficulty": 1
    },

    # ── PROGRAMMING CONCEPTS ──
    {
        "topic": "Programming Concepts",
        "subtopic": "OOP",
        "question_text": "Which OOP principle describes the ability of different classes to respond to the same method call in different ways?",
        "option_a": "Encapsulation",
        "option_b": "Inheritance",
        "option_c": "Abstraction",
        "option_d": "Polymorphism",
        "correct_answer": "D",
        "explanation": "Polymorphism (Greek: 'many forms') allows objects of different types to be treated as objects of a common type. A 'speak()' method on Animal objects can behave differently for Dog vs Cat.",
        "difficulty": 2
    },
    {
        "topic": "Programming Concepts",
        "subtopic": "OOP",
        "question_text": "What is Encapsulation in Object-Oriented Programming?",
        "option_a": "Creating multiple instances of a class",
        "option_b": "Inheriting properties from a parent class",
        "option_c": "Bundling data and methods together and restricting direct access",
        "option_d": "Writing functions with the same name but different parameters",
        "correct_answer": "C",
        "explanation": "Encapsulation bundles data (attributes) and methods (functions) into a class, and controls access using access modifiers (private, protected, public). This hides internal implementation details.",
        "difficulty": 2
    },
    {
        "topic": "Programming Concepts",
        "subtopic": "Recursion",
        "question_text": "What is a 'base case' in a recursive function?",
        "option_a": "The first line of the function",
        "option_b": "The condition that stops the recursion",
        "option_c": "The function calling itself",
        "option_d": "The return type of the function",
        "correct_answer": "B",
        "explanation": "A base case is the condition under which a recursive function stops calling itself and returns a value directly. Without a base case, the function would recurse infinitely and cause a stack overflow.",
        "difficulty": 1
    },
    {
        "topic": "Programming Concepts",
        "subtopic": "Memory",
        "question_text": "What is the difference between the Stack and Heap memory areas?",
        "option_a": "Stack is for global variables; Heap is for local variables",
        "option_b": "Stack manages function calls/local vars automatically; Heap is for dynamic allocation",
        "option_c": "Stack is slower than Heap",
        "option_d": "There is no difference; they are the same",
        "correct_answer": "B",
        "explanation": "The Stack automatically manages memory for function calls and local variables (freed when the function returns). The Heap is used for dynamic memory allocation (malloc, new) and must be manually managed.",
        "difficulty": 3
    },
]

# ── Knowledge Base Articles ──────────────────────────────
KNOWLEDGE_ARTICLES = [
    {
        "topic": "Data Structures",
        "title": "What is a Linked List?",
        "content": "A linked list is a linear data structure where elements (called nodes) are stored in non-contiguous memory locations. Each node contains two parts: the data and a pointer (reference) to the next node. Unlike arrays, linked lists do not need contiguous memory and can grow dynamically. The main types are: Singly Linked List (each node points to the next), Doubly Linked List (each node points to both next and previous), and Circular Linked List (last node points back to first). Linked lists are efficient for insertions and deletions at known positions (O(1)) but slow for random access (O(n)).",
        "keywords": "linked list, node, pointer, singly, doubly, circular, dynamic"
    },
    {
        "topic": "Data Structures",
        "title": "What is a Stack?",
        "content": "A stack is an abstract data type that follows the LIFO (Last In First Out) principle — the last element added is the first to be removed, like a stack of plates. The two main operations are PUSH (add to top) and POP (remove from top). PEEK lets you view the top without removing it. Stacks are used in: function call management (call stack), undo/redo operations, expression evaluation, backtracking algorithms, and browser history. Time complexity: push, pop, and peek are all O(1).",
        "keywords": "stack, LIFO, push, pop, peek, call stack, undo"
    },
    {
        "topic": "Data Structures",
        "title": "What is a Queue?",
        "content": "A queue is an abstract data type that follows the FIFO (First In First Out) principle — the first element added is the first to be removed, like a queue at a bus stop. The main operations are ENQUEUE (add to back) and DEQUEUE (remove from front). Queues are used in: task scheduling, CPU process scheduling, print spooling, breadth-first search, and message queues in distributed systems. Variants include: Priority Queue (elements have priority), Deque/Double-ended Queue (add/remove from both ends), and Circular Queue.",
        "keywords": "queue, FIFO, enqueue, dequeue, scheduling, BFS"
    },
    {
        "topic": "Algorithms",
        "title": "What is Big O Notation?",
        "content": "Big O notation is a mathematical notation used to describe the worst-case performance (upper bound) of an algorithm as the input size (n) grows. It ignores constants and lower-order terms to focus on the dominant growth factor. Common complexities from fastest to slowest: O(1) constant — same time regardless of n; O(log n) logarithmic — doubles input, adds one step (binary search); O(n) linear — time grows proportionally with n; O(n log n) — most efficient sorting algorithms; O(n²) quadratic — nested loops; O(2^n) exponential — brute-force combinatorics. Choosing an algorithm with better Big O can make the difference between a program running in milliseconds or days.",
        "keywords": "big O, complexity, time complexity, O(1), O(n), O(log n), algorithm analysis, efficiency"
    },
    {
        "topic": "Algorithms",
        "title": "How does Binary Search work?",
        "content": "Binary Search is an efficient algorithm for finding a target value in a SORTED array. It works by repeatedly dividing the search interval in half. Steps: 1) Set low=0, high=length-1. 2) Find middle index = (low+high)//2. 3) If array[middle] == target, return middle. 4) If target < array[middle], set high = middle-1 (search left half). 5) If target > array[middle], set low = middle+1 (search right half). 6) Repeat until found or low > high. Time complexity: O(log n). Example: Finding 73 in a 1000-element array takes at most 10 comparisons (log₂1000 ≈ 10) instead of up to 1000 with linear search.",
        "keywords": "binary search, sorted array, search algorithm, divide and conquer, O(log n)"
    },
    {
        "topic": "Algorithms",
        "title": "What is the difference between DFS and BFS?",
        "content": "DFS (Depth-First Search) and BFS (Breadth-First Search) are the two fundamental graph/tree traversal algorithms. BFS explores all neighbours at the current depth before moving deeper — it uses a Queue and finds the shortest path in unweighted graphs. DFS explores as far as possible along one branch before backtracking — it uses a Stack (or recursion) and is useful for cycle detection, topological sorting, and maze solving. BFS is generally better for finding shortest paths; DFS uses less memory on wide graphs. Both have O(V+E) time complexity where V=vertices and E=edges.",
        "keywords": "DFS, BFS, depth first, breadth first, traversal, graph, tree, shortest path"
    },
    {
        "topic": "Databases",
        "title": "What is SQL and what are the main commands?",
        "content": "SQL (Structured Query Language) is the standard language for interacting with relational databases. The main categories of SQL commands are: DDL (Data Definition Language) — CREATE TABLE, ALTER TABLE, DROP TABLE; DML (Data Manipulation Language) — SELECT (read), INSERT (create), UPDATE (modify), DELETE (remove); DCL (Data Control Language) — GRANT, REVOKE; TCL (Transaction Control Language) — COMMIT, ROLLBACK. A basic SELECT query: SELECT column1, column2 FROM table_name WHERE condition ORDER BY column1 LIMIT 10; SQL is used by databases like PostgreSQL, MySQL, SQLite, and Microsoft SQL Server.",
        "keywords": "SQL, SELECT, INSERT, UPDATE, DELETE, CREATE TABLE, DDL, DML, query, database"
    },
    {
        "topic": "Databases",
        "title": "What is Database Normalisation?",
        "content": "Database normalisation is the process of organising a relational database to reduce data redundancy and improve data integrity. It involves dividing large tables into smaller ones and defining relationships. The normal forms are: 1NF (First Normal Form) — each column contains atomic (indivisible) values, no repeating groups; 2NF — in 1NF and every non-key attribute is fully dependent on the entire primary key; 3NF — in 2NF and no transitive dependencies (non-key column depending on another non-key column); BCNF (Boyce-Codd) — a stronger version of 3NF. Proper normalisation prevents INSERT, UPDATE, and DELETE anomalies.",
        "keywords": "normalisation, normalization, 1NF, 2NF, 3NF, BCNF, redundancy, data integrity, normal forms"
    },
    {
        "topic": "Programming Concepts",
        "title": "What are the 4 pillars of OOP?",
        "content": "Object-Oriented Programming (OOP) is based on four fundamental principles: 1) Encapsulation — bundling data and methods into a class, hiding internal details using access modifiers (private/public/protected). Example: a BankAccount class hides the balance and only exposes deposit() and withdraw() methods. 2) Inheritance — a child class acquires properties and methods from a parent class, enabling code reuse. Example: Dog and Cat inherit from Animal. 3) Polymorphism — the same interface works differently for different types. Example: animal.speak() outputs 'Woof' for Dog and 'Meow' for Cat. 4) Abstraction — hiding complex implementation details and showing only essential features. Example: you drive a car without knowing how the engine works.",
        "keywords": "OOP, encapsulation, inheritance, polymorphism, abstraction, class, object, pillars"
    },
    {
        "topic": "Programming Concepts",
        "title": "What is recursion and when should you use it?",
        "content": "Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem. Every recursive function needs: 1) A base case — the condition that stops recursion (prevents infinite loop). 2) A recursive case — where the function calls itself with a smaller/simpler input. Classic examples: factorial(n) = n × factorial(n-1), Fibonacci sequence, tree traversal, merge sort. When to use recursion: naturally recursive problems like trees/graphs, divide-and-conquer algorithms, problems that can be broken into identical subproblems. When NOT to use: when an iterative solution is simpler, or when the recursion depth is very large (risk of stack overflow). Recursion can always be converted to iteration using an explicit stack.",
        "keywords": "recursion, recursive, base case, stack overflow, factorial, fibonacci, divide and conquer"
    },
]


def seed():
    """Insert all sample data into the database"""
    with app.app_context():
        # Only seed if tables are empty
        if Question.query.count() == 0:
            print("📝 Seeding quiz questions...")
            for q_data in QUESTIONS:
                question = Question(**q_data)
                db.session.add(question)
            db.session.commit()
            print(f"   ✅ Added {len(QUESTIONS)} questions.")
        else:
            print("   ⏭️  Questions already exist, skipping.")

        if KnowledgeArticle.query.count() == 0:
            print("📚 Seeding knowledge base articles...")
            for a_data in KNOWLEDGE_ARTICLES:
                article = KnowledgeArticle(**a_data)
                db.session.add(article)
            db.session.commit()
            print(f"   ✅ Added {len(KNOWLEDGE_ARTICLES)} articles.")
        else:
            print("   ⏭️  Articles already exist, skipping.")

        print("\n🎉 Database seeding complete!")


if __name__ == "__main__":
    seed()
