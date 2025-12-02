from googletrans import Translator

translator = Translator()

test_texts = {
    "Chinese": "这是一个很棒的项目，用于机器学习和人工智能",
    "Korean": "이것은 머신러닝과 인공지능을 위한 훌륭한 프로젝트입니다",
    "Spanish": "Este es un excelente proyecto para aprendizaje automático e inteligencia artificial",
    "French": "C'est un excellent projet pour l'apprentissage automatique et l'intelligence artificielle",
    "German": "Dies ist ein ausgezeichnetes Projekt für maschinelles Lernen und künstliche Intelligenz",
    "Japanese": "これは機械学習と人工知能のための素晴らしいプロジェクトです"
}

print("translation test\n" + "="*60 + "\n")

for language, text in test_texts.items():
    print(f"{language}:")
    print(f"  original: {text}")
    
    try:
        translated = translator.translate(text, dest='en')
        print(f"  english:  {translated.text}\n")
    except Exception as e:
        print(f"  error: {e}\n")

##########################################################################################
# output:
##########################################################################################
# Chinese:
#   original: 这是一个很棒的项目，用于机器学习和人工智能
#   english:  This is a great project for machine learning and artificial intelligence

# Korean:
#   original: 이것은 머신러닝과 인공지능을 위한 훌륭한 프로젝트입니다
#   english:  This is a great project for machine learning and artificial intelligence

# Spanish:
#   original: Este es un excelente proyecto para aprendizaje automático e inteligencia artificial
#   english:  This is an excellent project for machine learning and artificial intelligence

# French:
#   original: C'est un excellent projet pour l'apprentissage automatique et l'intelligence artificielle
#   english:  This is a great project for machine learning and artificial intelligence

# German:
#   original: Dies ist ein ausgezeichnetes Projekt für maschinelles Lernen und künstliche Intelligenz
#   english:  This is an excellent machine learning and artificial intelligence project

# Japanese:
#   original: これは機械学習と人工知能のための素晴らしいプロジェクトです
#   english:  This is a great project for machine learning and artificial intelligence