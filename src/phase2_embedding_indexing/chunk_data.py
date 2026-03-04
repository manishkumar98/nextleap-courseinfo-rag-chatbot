import json
import os

def load_raw_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def create_chunks_with_sources(data):
    """
    Transforms the raw course data into smaller semantic chunks.
    Crucially, each chunk retains the 'url' metadata for RAG citations.
    """
    chunks = []
    
    for course in data['courses']:
        course_name = course['title']
        url = course['url']
        
        # 1. Chunk: General Info
        chunks.append({
            "text": f"{course_name} Overview: Duration {course['duration']}, Live Hours {course['live_hours']}. Next cohort starts {course['next_cohort']}.",
            "metadata": {
                "source_url": url,
                "category": "overview",
                "course": course_name
            }
        })
        
        # 2. Chunk: Cost & Deadlines
        chunks.append({
            "text": f"{course_name} Cost: Base price is {course['base_cost']}, discounted to {course['discounted_cost']}. Price increase deadline: {course['deadline']}.",
            "metadata": {
                "source_url": url,
                "category": "pricing",
                "course": course_name
            }
        })
        
        # 3. Chunk: Instructors
        instructor_list = ", ".join(course['instructors'])
        chunks.append({
            "text": f"Instructors and Mentors for {course_name}: {instructor_list}.",
            "metadata": {
                "source_url": url,
                "category": "instructors",
                "course": course_name
            }
        })
        
        # 4. Chunk: Outcomes
        chunks.append({
            "text": f"{course_name} Outcomes: Average Salary {course['avg_salary']}, Highest Salary {course['highest_salary']}. Placement Support: {course['placement_support']}.",
            "metadata": {
                "source_url": url,
                "category": "outcomes",
                "course": course_name
            }
        })

        # 5. Chunk: Curriculum / Syllabus (Enriched with Keywords)
        if 'curriculum' in course:
            # Map course titles to abbreviations for better retrieval
            abbreviations = {
                "Product Manager Fellowship": "PM",
                "UI/UX Designer Fellowship": "UX / UI Design",
                "Data Analyst Fellowship": "DA",
                "Business Analyst Fellowship": "BA",
                "Applied Generative AI Bootcamp": "GenAI / AI"
            }
            abbr = abbreviations.get(course_name, "")
            
            for item in course['curriculum']:
                chunks.append({
                    "text": f"{course_name} ({abbr}) Curriculum & Syllabus - {item}",
                    "metadata": {
                        "source_url": url,
                        "category": "curriculum",
                        "course": course_name
                    }
                })

    # 5. Terminology chunks
    if 'terminology' in data:
        for item in data['terminology']:
            chunks.append({
                "text": f"Knowledge Item - {item['term']}: {item['meaning']} Context: {item['context']}",
                "metadata": {
                    "source_url": "https://nextleap.app/about",
                    "category": "terminology",
                    "term": item['term']
                }
            })

    return chunks

if __name__ == "__main__":
    # Corrected Absolute Paths
    input_file = "/Users/binaykumarsinha/Desktop/AIBootcampProject/nextleap-rag-chatbot-1/src/phase1_data_acquisition/raw_nextleap_data.json"
    output_file = "/Users/binaykumarsinha/Desktop/AIBootcampProject/nextleap-rag-chatbot-1/data/course_chunks.json"
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    if os.path.exists(input_file):
        raw_data = load_raw_data(input_file)
        processed_chunks = create_chunks_with_sources(raw_data)
        
        with open(output_file, 'w') as f:
            json.dump(processed_chunks, f, indent=2)
        print(f"✅ Successfully created {len(processed_chunks)} chunks with source URLs.")
    else:
        print("❌ Error: raw_nextleap_data.json not found.")
