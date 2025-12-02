import sys
sys.path.insert(0, '..')
from mongodb_storage import MongoDBStorage

def view_recent_repos(db):
    repos = db.get_recent_repos(10)
    print(f"\n recent {len(repos)} GitHub repos:\n")
    for i, repo in enumerate(repos, 1):
        print(f"{i}. {repo['full_name']}")
        print(f"     {repo['stars_total']} stars | 🔧 {repo['language']}")
        print(f"     {repo['description'][:80]}...\n")

def view_repos_by_language(db):
    lang = input("enter language (e.g., Python, JavaScript): ").strip()
    repos = db.get_repos_by_language(lang)
    print(f"\n {len(repos)} {lang} repos:\n")
    for i, repo in enumerate(repos, 1):
        print(f"{i}. {repo['full_name']}   {repo['stars_total']}\n")

def view_recent_papers(db):
    papers = list(db.arxiv_collection.find().sort("scraped_at", -1).limit(10))
    print(f"\n recent {len(papers)} arXiv papers:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:2])}...")
        print(f"   Published: {paper['published']}\n")

def view_papers_by_category(db):
    cat = input("enter category (e.g., cs.AI, cs.LG): ").strip()
    papers = db.get_papers_by_category(cat)
    print(f"\n {len(papers)} papers in {cat}:\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper['title']}\n")

def main():
    db = MongoDBStorage()
    print("\n" + "="*60)
    print("GEN-EEZES DATA VIEWER")
    print("="*60 + "\n")
    
    options = {
        "1": view_recent_repos,
        "2": view_repos_by_language,
        "3": view_recent_papers,
        "4": view_papers_by_category,
        "5": lambda db: db.get_collection_stats()
    }
    
    while True:
        print("1. view recent GitHub repos")
        print("2. view repos by language")
        print("3. view recent arXiv papers")
        print("4. view papers by category")
        print("5. view collection stats")
        print("6. exit\n")
        choice = input("choose option (1-6): ").strip()
        
        if choice in options:
            options[choice](db)
        elif choice == "6":
            print("exiting...\n")
            break
        else:
            print(" invalid option\n")

if __name__ == "__main__":
    main()