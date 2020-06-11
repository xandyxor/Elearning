from django.shortcuts import render,redirect,get_object_or_404

from django.http import HttpResponse

# Create your views here.

from course.models import Course,Lesson,Words,Examples

from course.forms import CourseForm

from django.contrib import messages

from django.db.models.query_utils import Q

from django.views.generic.base import View

from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from googletrans import Translator
translator = Translator()

class indexView(View):
    '''
    顯示首頁
    '''
    def get(self,request):
        # return render(request, 'login.html')
        courses = {}
        for course in Course.objects.all():
            courses.update({course:Lesson.objects.filter(course=course)})

        # articles = {}
        # for article in Article.objects.all():
        #     articles.update({article:Comment.objects.filter(article=article)})

        context = {'courses':courses}
        # print(context)
        return render(request, 'course/index.html', context)

# class dashboardView(View):
#     '''
#     顯示dashboard
#     '''
#     def get(self,request):
#         # return render(request, 'login.html')
#         courses = {}
#         for course in Course.objects.all():
#             courses.update({course:Lesson.objects.filter(course=course)})

#         # articles = {}
#         # for article in Article.objects.all():
#         #     articles.update({article:Comment.objects.filter(article=article)})

#         context = {'courses':courses}
#         # print(context)
#         return render(request, 'course/sbadmin2.html', context)


def example_generator(input_word):
    translator = Translator()
    translations = translator.translate(input_word,src='en',dest='zh-tw')
    translations_dict = translations.extra_data
    examples_len = len(translations_dict['examples'])

    if examples_len > 0:
        examples_len = len(translations_dict['examples'][0])
    else:
        print('沒有例句')
    # 還原詞性

    from nltk.corpus import wordnet
    from nltk import word_tokenize, pos_tag
    from nltk.stem import WordNetLemmatizer


    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None


    def lemmatize_sentence(sentence):
        # res = []
        res = {}
        row_sentence=[]
        lemmatizer = WordNetLemmatizer()
        for word, pos in pos_tag(word_tokenize(sentence)):
            wordnet_pos = get_wordnet_pos(pos) or wordnet.NOUN
            # res.append(lemmatizer.lemmatize(word, pos=wordnet_pos))
            row_sentence.append(word)
            res.update({lemmatizer.lemmatize(word, pos=wordnet_pos):wordnet_pos})
        return row_sentence,res

    import codecs
    word_dict={}
    cont=''
    wd_adjective=[]
    wd_noun=[]
    wd_verb=[]
    wd_adverb=[]

    with codecs.open('7000單字.txt', 'r', encoding='utf8') as f:
        for line in f:
            tmp = line.split('\t')
            word_dict.update({tmp[0]:tmp[1]})
            if tmp[1]=='a' or tmp[1]=='adj.':
                wd_adjective.append(tmp[0])
            elif tmp[1] == 'n' or tmp[1] == 'n.' or tmp[1] == 'N':
                wd_noun.append(tmp[0])
            elif tmp[1] == 'v' :
                wd_verb.append(tmp[0])
            elif tmp[1] == 'r' or tmp[1] == 'adv' or tmp[1] == 'adv.':
                wd_adverb.append(tmp[0])
            


    tag_2google = {
                'a':'adjective',
                'n':'noun',
                'v':'verb',
                'r':'adverb'
            }
    def hava_difficult_words(row_words,lemmatize_words): #檢查句子 有無沒有在7000單字裡的難字 並回傳json
        output_json={}
        difficult=0
        ez=0
        for i in range(len(lemmatize_words)):
            # row_word = list(res.keys())[i] #為啥要這樣寫?
            lemmatize_word = list(lemmatize_words.keys())[i]
            if lemmatize_word.isalpha(): #判斷是否是英文
                if lemmatize_word.lower() in word_dict: #判斷是否有在7000單字內
                    ez += 1
                elif lemmatize_word.istitle(): #判斷是否首字大寫，大寫的話代表專有名詞
                    if i==1: #句子開頭
                        # print("difficult:",row_word)
                        # print(list(res.values())[i])
                        output_json.update({difficult:{'difficult':row_words[i],'tag':tag_2google[list(lemmatize_words.values())[i]]}})
                        difficult+=1
                    else:
                        ez += 1
                        #因為既然不在7000單字內，而且又不是句子開頭那就代表是專有名詞，不須替換
                else:
                    # print("difficult:",row_word)
                    # print(list(res.values())[i])
                    output_json.update({difficult:{'difficult':row_words[i],'tag':tag_2google[list(lemmatize_words.values())[i]]}})
                    difficult+=1
        return output_json

    def nltk_synonyms(difficult_words_json):
        # 如果有非7000單字 就去搜尋同意字替換
        # nltk方法
        
        import nltk 
        from nltk.corpus import wordnet 

        output_json={}

        for i in difficult_words_json:
            word_synonyms = []
            for syn in wordnet.synsets(difficult_words_json[i]['difficult']): 
                for l in syn.lemmas():
                    if (l.name().lower() in word_dict) and (l.name().lower() != difficult_words_json[i]['difficult']) and not (l.name().lower() in word_synonyms):
                        # 如果有在7000單字內 且 不重複
                        word_synonyms.append(l.name().lower())
            output_json.update({i:word_synonyms})

        return output_json

    def google_synonyms(difficult_words_json):
        output_json={}
        for i in difficult_words_json:
            synonyms_translations = translator.translate(difficult_words_json[i]['difficult'],src='en',dest='zh-tw')
            synonyms_translations_dict = synonyms_translations.extra_data
            word_synonyms = []
            tag_flag = ''
            for j in difficult_words_json: #因為不是len判斷，所以可能會有非數字的情形這樣的話程式就會出錯
                if synonyms_translations_dict['synonyms'] != None:
                    for tags in synonyms_translations_dict['synonyms']:
                        for tag in tags:
                            if isinstance(tag,str):
                                #print('tag',tag)
                                tag_flag = tag   
                            elif isinstance(tag,list):
                                for synonyms in tag:
                                    for words in synonyms:
                                        if isinstance(words,list):
                                            for word in words:
                                                #print('word',word)
                                                if (tag_flag == difficult_words_json[j]['tag']) and (word in word_dict) and not (word in word_synonyms): #如果是相同詞性而且是在7000單字裡
                                                    word_synonyms.append(word)
            output_json.update({i:word_synonyms})  
        return output_json


    # for examples_len in range(len(translations_dict['examples'][0]) if len(translations_dict['examples'][0])<30 else 30):
    output_examples=[]
    output_json={}
    i = 0
    for examples_len in range(len(translations_dict['examples'][0])):
        
        example = translations_dict['examples'][0][examples_len][0]
        example = (example[:example.find('<b>')]+ input_word +example[example.find('</b>')+4:])
        row_words,lemmatize_words = lemmatize_sentence(example)
        
        difficult_words_json = hava_difficult_words(row_words,lemmatize_words)
        if difficult_words_json == {}:
            # print("全句都符合7000單字難度",example)
            output_examples.append(example)
            output_json.update(
                {
                    i:{
                        'example':example,
                        'difficults':None,
                        'nltk':None,
                        'google':None
                    }
                }
            )
            i+=1
        else:   
            # print(difficult_words_json,example)
            from_nltk_synonyms = nltk_synonyms(difficult_words_json)
            from_google_synonyms = google_synonyms(difficult_words_json)
            if (from_nltk_synonyms != {0: []}) or (from_google_synonyms != {0: []}):
                # print(from_nltk_synonyms) 
                # print(from_google_synonyms)
                output_json.update(
                    {
                        i:{
                            'example':example,
                            'difficults':difficult_words_json,
                            'nltk':from_nltk_synonyms,
                            'google':from_google_synonyms
                        }
                    }
                )
                i+=1
    return output_json


def example_sentence_generator(word_example_generator):
    import random
    random_sentence_int = random.randint(0,len(word_example_generator)-1) #隨機選一個範例句子
    example_sentence = word_example_generator[random_sentence_int]['example'] #挑選出來的句子
    tmp_dict=[]
    output_sentence=''
    if word_example_generator[random_sentence_int]['difficults'] == None: #如果沒有難字(不在7000單字內)就直接輸出吧
        #print('row',example_sentence)
        output_sentence = example_sentence
    else:
        for word_lists_int in range(0,len(word_example_generator[random_sentence_int]['difficults'])):
            tmp_dict=[] 
            #print(word_lists_int)
            if word_example_generator[random_sentence_int]['nltk'][word_lists_int] != []: #如果難字是有可替換的單字(從nltk找同義字)
                for word in (word_example_generator[random_sentence_int]['nltk'][word_lists_int]): #把可替換字加入至待挑選的字典
                    tmp_dict.append(word)
            if word_example_generator[random_sentence_int]['google'][word_lists_int] != []:
                for word in (word_example_generator[random_sentence_int]['google'][word_lists_int]):
                    tmp_dict.append(word)

            if tmp_dict!=[]: #如果待挑選字典不是空的(有可挑選的同義字
                if output_sentence=='':
                    find_int = example_sentence.find(word_example_generator[random_sentence_int]['difficults'][word_lists_int]['difficult']) #尋找取代原本例句難字的位子
                    difficult_word_len = len(word_example_generator[random_sentence_int]['difficults'][word_lists_int]['difficult']) #該原文難字的長度
                    output_sentence = example_sentence[:find_int]+tmp_dict[random.randint(0,len(tmp_dict)-1)]+example_sentence[find_int+difficult_word_len:] #替換句子
                    #print(output_sentence)
                else:
                    find_int = output_sentence.find(word_example_generator[random_sentence_int]['difficults'][word_lists_int]['difficult']) #尋找取代原本例句難字的位子
                    difficult_word_len = len(word_example_generator[random_sentence_int]['difficults'][word_lists_int]['difficult']) #該原文難字的長度
                    output_sentence = output_sentence[:find_int]+tmp_dict[random.randint(0,len(tmp_dict)-1)]+output_sentence[find_int+difficult_word_len:] #替換句子
                    #print(output_sentence)
            else:
                #print('row',example_sentence)
                output_sentence = example_sentence
    print(output_sentence)
    return output_sentence


def dashboardView(request):
    '''
    顯示dashboard
    '''
    # return render(request, 'login.html')
    courses = {}
    for course in Course.objects.all():
        courses.update({course:Lesson.objects.filter(course=course)})

    # articles = {}
    # for article in Article.objects.all():
    #     articles.update({article:Comment.objects.filter(article=article)})

    context = {'courses':courses}
    # print(context)
    return render(request, 'course/sbadmin2.html', context)


def course(request):
    '''
    Render the course page
    '''
    # courses = Course.objects.all()


    courses = {}
    for course in Course.objects.all():
        courses.update({course:Lesson.objects.filter(course=course)})

    # articles = {}
    # for article in Article.objects.all():
    #     articles.update({article:Comment.objects.filter(article=article)})
    print(courses)
    context = {'courses':courses}
    # print(context)
    return render(request, 'course/course.html', context)


def addcourse(request):
    '''
    Create a new article instance
        1. If method is GET, render an empty form
        2. If method is POST, perform form validation and display error messages if the form is invalid
        3. Save the form to the model and redirect the user to the article page
    '''
    # TODO: finish the code
    # return render(request, 'course/course.html')
    template = 'course/addcourse.html'
    # template = 'courses/coursesUpdate.html'
    if request.method == 'GET':
        return render(request, template, {'courseForm':CourseForm()})
        
    # POST
    courseForm = CourseForm(request.POST)
    if not courseForm.is_valid():
        return render(request, template, {'courseForm':courseForm})

    courseForm.save()
    # return course(request)
    messages.success(request, '課程已新增')
    return redirect('course:course')


def courseRead(request, courseId):
    '''
    Read an article
        1. Get the "article" instance using "articleId"; redirect to the 404 page if not found
        2. Render the articleRead template with the article instance and its
           associated comments
    '''
    course = get_object_or_404(Course, id=courseId)
    context = {
        'course': course,
        'lessons': Lesson.objects.filter(course=course)
    }
    return render(request, 'course/courseRead.html', context)


def courseUpdate(request, courseId):
    '''
    Update the article instance:
        1. Get the article to update; redirect to 404 if not found
        2. Render a bound form if the method is GET
        3. If the form is valid, save it to the model, otherwise render a
           bound form with error messages
    '''
    course = get_object_or_404(Course, id=courseId)
    template = 'course/courseUpdate.html'
    if request.method == 'GET':
        courseForm = CourseForm(instance=course)
        return render(request, template, {'courseForm':courseForm})

    # POST
    courseForm = CourseForm(request.POST, instance=course)
    if not courseForm.is_valid():
        return render(request, template, {'courseForm':courseForm})

    courseForm.save()
    messages.success(request, '課程已修改') 
    return redirect('course:courseRead', courseId=courseId)


def courseDelete(request, courseId):
    '''
    Delete the article instance:
        1. Render the article page if the method is GET
        2. Get the article to delete; redirect to 404 if not found
    '''

    if request.method == 'GET':
        return redirect('course:course')

    # POST
    course = get_object_or_404(Course, id=courseId)
    course.delete()
    messages.success(request, '文章已刪除')  
    return redirect('course:course')


def courseSearch(request):
    '''
    Search for articles:
        1. Get the "searchTerm" from the HTML page
        2. Use "searchTerm" for filtering
    '''
    searchTerm = request.GET.get('searchTerm')
    courses = Course.objects.filter(Q(name__icontains=searchTerm) |
                                      Q(desc__icontains=searchTerm))
    context = {'courses':courses, 'searchTerm':searchTerm} 
    return render(request, 'course/courseSearch.html', context)


def courseLike(request, courseId):
    '''
    Add the user to the 'likes' field:
        1. Get the article; redirect to 404 if not found
        2. If the user does not exist in the "likes" field, add him/her
        3. Finally, call articleRead() function to render the article
    '''
    
    course = get_object_or_404(Course, id=courseId)
    # print(course.likes.all())
    # print(request.user.course_set.all() )
    if request.user not in course.likes.all():
        course.likes.add(request.user)
    return courseRead(request, courseId)

def GeneratedSentences(request):
    '''
    GeneratedSentences
    '''
    return render(request, 'course/Generated Sentences.html',)

def courseRead_new(request,courseId):
    '''
    顯示courseRead_new
    '''
    # 無單字版本
    course = get_object_or_404(Course, id=courseId)
    context = {
        'course': course,
        'lessons': Lesson.objects.filter(course=course)
    }

    # course = get_object_or_404(Course, id=courseId)
    # 有單字版本
    # lessons = {}  
    # for lesson in Lesson.objects.all():
    #     lessons.update({lesson:Words.objects.filter(lesson=lesson)})
    # context = {
    #     'course':course,
    #     'lessons':lessons
    #     }
    # print(context)
    
    return render(request, 'course/courseRead(new).html', context)


def lessonRead(request,lessonId):
    '''
    顯示lessonRead
    '''
    # 無單字版本
    lesson = get_object_or_404(Lesson, id=lessonId)
    context = {
        'lesson': lesson,
        'words': Words.objects.filter(lesson=lesson)
    }

    # course = get_object_or_404(Course, id=courseId)
    # 有單字版本
    # lessons = {}  
    # for lesson in Lesson.objects.all():
    #     lessons.update({lesson:Words.objects.filter(lesson=lesson)})
    # context = {
    #     'course':course,
    #     'lessons':lessons
    #     }
    # print(context)

    return render(request, 'course/lessonRead.html', context)


def Sentence_old(request,courseId):
    '''
    顯示courseRead_new
    '''
    # course = get_object_or_404(Course, id=courseId)
    # context = {
    #     'course': course,
    #     'lessons': Lesson.objects.filter(course=course)
    # }


    course = get_object_or_404(Course, id=courseId)
    lessons = {}
    example = []
    for lesson in Lesson.objects.all():
        # print(Words.objects.filter(lesson=lesson))
        a = Words.objects.filter(lesson=lesson)
        for e in a:
            # print(e.example)
            example.append(e.example)
        lessons.update({lesson:Words.objects.filter(lesson=lesson)})
    print(example)
    # ['One of the best known of Aesop\'s fables is "The Lion and the Mouse."', 'The moral of "The Lion and the Mouse" is: Little friends may prove to be great friends.']
    
    

    '''
        判斷詞性部分
    '''
    from textblob import TextBlob

    text = example[0]

    '''
        google翻譯
    '''
    # from py_translator import TEXTLIB
    # s = TEXTLIB().translator(is_html=False, text= example[0] , lang_to='zh-TW', proxy=False)

    s = translator.translate(example[0], dest='zh-tw',src='en')

    print(s)
    example_tw = s.text


    blob = TextBlob(text)
    # print(blob.tags)           # [('The', 'DT'), ('titular', 'JJ'),
                        #  ('threat', 'NN'), ('of', 'IN'), ...]
    words_tag_2_tw={

        'CC':'並列連詞',
        'CD':'純數,基數',
        'DT':'限定詞(置於名詞前起限定作用,如 the、some、my 等)',
        'EX':'存在句,存現句',
        'FW':'外來語',
        'IN':'介詞/從屬連詞,主從連詞,從屬連接詞',
        'JJ':'形容詞',
        'JJR':'（形容詞或副詞的）比較級形式',
        'JJS':'（形容詞或副詞的）最高級',
        'LS':'listmarker',
        'MD':'形態的，形式的 , 語氣的；情態的',
        'NN':'名詞單數形式',
        'NNS':'名詞複數形式',
        'NNP':'專有名詞',
        'NNPS':'專有名詞複數形式',
        'PDT':"前位限定詞",
        'POS':'屬有詞,結束語',
        'PRP':'人稱代詞',
        'PRP$':'物主代詞',
        'RB':'副詞',
        'RBR':'（形容詞或副詞的）比較級形式',
        'RBS':'（形容詞或副詞的）最高級',
        'RP':'小品詞(與動詞構成短語動詞的副詞或介詞)',
        'TO':'to',
        'UH':'感嘆詞；感嘆語',
        'VB':'動詞',
        'VBD':'動詞,過去時,過去式',
        'VBG':'動詞 ,動名詞/現在分詞',
        'VBN':'動詞,過去分詞',
        'VBP':'動詞,現在',
        'VBZ':'動詞,第三人稱',
        'WDT':'限定詞（置於名詞前起限定作用，如 the、some、my 等）',
        'WP':'代詞（代替名詞或名詞詞組的單詞）',
        'WP$':'所有格；屬有詞',
        'WRB':'副詞'
    }

    # all_tag='''
    #     <option value="名詞">名詞</option>
    #     <option value="CC">並列連詞</option>
    #     <option value="CD">純數,基數</option>
    #     <option value="DT">限定詞(置於名詞前起限定作用)</option>
    #     <option value="EX">存在句,存現句</option>
    #     <option value="FW">外來語</option>
    #     <option value="IN">介詞/從屬連詞,主從連詞,從屬連接詞</option>
    #     <option value="JJ">形容詞</option>
    #     <option value="JJR">（形容詞或副詞的）比較級形式</option>
    #     <option value="JJS">（形容詞或副詞的）最高級</option>
    #     <option value="LS">listmarker</option>
    #     <option value="MD">形態的，形式的,語氣的；情態的</option>
    #     <option value="NN">名詞單數形式</option>
    #     <option value="NNS">名詞複數形式</option>
    #     <option value="NNP">專有名詞</option>
    #     <option value="NNPS">專有名詞複數形式</option>
    #     <option value="PDT">前位限定詞</option>
    #     <option value="POS">屬有詞,結束語</option>
    #     <option value="PRP">人稱代詞</option>
    #     <option value="PRP$">物主代詞</option>
    #     <option value="RB">副詞</option>
    #     <option value="RBR">（形容詞或副詞的）比較級形式</option>
    #     <option value="RBS">（形容詞或副詞的）最高級</option>
    #     <option value="RP">小品詞(與動詞構成短語動詞的副詞或介詞)</option>
    #     <option value="TO">to</option>
    #     <option value="UH">感嘆詞；感嘆語</option>
    #     <option value="VB">動詞</option>
    #     <option value="VBD">動詞,過去時,過去式</option>
    #     <option value="VBG">動詞 ,動名詞/現在分詞</option>
    #     <option value="VBN">動詞,過去分詞</option>
    #     <option value="VBP">動詞,現在</option>
    #     <option value="VBZ">動詞,第三人稱</option>
    #     <option value="WDT">限定詞（置於名詞前起限定作用，如 the、some、my 等）</option>
    #     <option value="WP">代詞（代替名詞或名詞詞組的單詞）</option>
    #     <option value="WP$">所有格；屬有詞</option>
    #     <option value="WRB">副詞'</option>
    # '''


    # CC     coordinating conjunction 並列連詞
    # CD     cardinaldigit  純數  基數
    # DT     determiner  限定詞（置於名詞前起限定作用，如 the、some、my 等）
    # EX     existentialthere (like:"there is"... think of it like "thereexists")   存在句；存現句
    # FW     foreignword  外來語；外來詞；外文原詞
    # IN     preposition/subordinating conjunction介詞/從屬連詞；主從連詞；從屬連接詞
    # JJ     adjective    'big'  形容詞
    # JJR    adjective, comparative 'bigger' （形容詞或副詞的）比較級形式
    # JJS    adjective, superlative 'biggest'  （形容詞或副詞的）最高級
    # LS     listmarker  1)
    # MD     modal (could, will) 形態的，形式的 , 語氣的；情態的
    # NN     noun, singular 'desk' 名詞單數形式
    # NNS    nounplural  'desks'  名詞複數形式
    # NNP    propernoun, singular     'Harrison' 專有名詞
    # NNPS  proper noun, plural 'Americans'  專有名詞複數形式
    # PDT    predeterminer      'all the kids'  前位限定詞
    # POS    possessiveending  parent's   屬有詞  結束語
    # PRP    personalpronoun   I, he, she  人稱代詞
    # PRP$  possessive pronoun my, his, hers  物主代詞
    # RB     adverb very, silently, 副詞    非常  靜靜地
    # RBR    adverb,comparative better   （形容詞或副詞的）比較級形式
    # RBS    adverb,superlative best    （形容詞或副詞的）最高級
    # RP     particle     give up 小品詞(與動詞構成短語動詞的副詞或介詞)
    # TO     to    go 'to' the store.
    # UH     interjection errrrrrrrm  感嘆詞；感嘆語
    # VB     verb, baseform    take   動詞
    # VBD    verb, pasttense   took   動詞   過去時；過去式
    # VBG    verb,gerund/present participle taking 動詞  動名詞/現在分詞
    # VBN    verb, pastparticiple     taken 動詞  過去分詞
    # VBP    verb,sing. present, non-3d     take 動詞  現在
    # VBZ    verb, 3rdperson sing. present  takes   動詞  第三人稱
    # WDT    wh-determiner      which 限定詞（置於名詞前起限定作用，如 the、some、my 等）
    # WP     wh-pronoun   who, what 代詞（代替名詞或名詞詞組的單詞）
    # WP$    possessivewh-pronoun     whose  所有格；屬有詞
    # WRB    wh-abverb    where, when 副詞




    sentence = ''
    
    # for word,tag in  blob.tags:
    #     sentence += '''
    #     <form>
    #         <div class="form-row align-items-center">
    #         <div class="col-auto my-1">
    #             <label class="mr-sm-2" for="inlineFormCustomSelect">
    #     '''
    #     sentence += word

    #     sentence += '''
    #             </label>
    #             <select class="custom-select mr-sm-2" id="inlineFormCustomSelect">
    #     '''
    #     sentence += '<option selected value="'+tag+'" >'+tag+'</option>'

    #     sentence += '''
    #             <option value="名詞">名詞</option>
    #             <option value="動詞">動詞</option>
    #             </select>
    #         </div>
            
    #         <div class="col-auto my-1">
    #             <button type="submit" class="btn btn-primary">Submit</button>
    #         </div>
    #         </div>
    #     </form>
    #     '''
        # print(word,tag)

    # sentence += '''
    #     <form>
    #         <div class="row">    
    # '''
  
    # for word,tag in  blob.tags:   
    #     sentence += '''
    #             <div class="form-row align-items-center">
    #                 <div class="col-2"> 
    #     '''
    #     sentence += '<label class="mr-sm-2" for="inlineFormCustomSelect">'+word+'</label>'
    #     sentence += '''
    #             <select id="select_words" name="town" style="font-size:6px;">
    #     '''
    #     sentence += '<option value="'+tag+'">'+words_tag_2_tw[tag]+'</option>'
    #     sentence += all_tag
    #     sentence += '''
    #             </select>
    #             </div>
    #         </div>
    #     '''
    # sentence += '''    
    #         </div>
    #     </form>
    # '''
    
    # '''html
    # <form>
    #     <div class="form-row align-items-center">
    #         <div class="col-4">
    #             <label class="mr-sm-2" for="inlineFormCustomSelect">words</label>
    #             <select id="select_words" name="town" style="font-size:12px;">
    #                 <option value="名詞">名詞</option>
    #                 <option value="動詞">動詞</option>
    #             </select>
    #         </div>
    #     </div>
    # </form>
    # '''

    sentence += '''
        <div class="row"> 
    '''
  
    for word,tag in  blob.tags:
        if word == "'s":
            sentence += '<font  data-toggle="tooltip" data-html="true" title="'+words_tag_2_tw[tag]+'">'+word+'</font >'
        else:
            sentence += '<font  data-toggle="tooltip" data-html="true" title="'+words_tag_2_tw[tag]+'">&nbsp;'+word+'</font >'

    sentence += '''   
        </div>
        <div class="row"> 
            '''+example_tw+'''
        </div>
    '''
    
    # '''html
    # <div class="row">
    #     <label class="mr-sm-2" for="inlineFormCustomSelect" data-toggle="tooltip" data-html="true" title="12312313">words</label>
    #     <label class="mr-sm-2" for="inlineFormCustomSelect" data-toggle="tooltip" data-html="true" title="12312313">words</label>
    #     <label class="mr-sm-2" for="inlineFormCustomSelect" data-toggle="tooltip" data-html="true" title="12312313">words</label>
    #     <label class="mr-sm-2" for="inlineFormCustomSelect" data-toggle="tooltip" data-html="true" title="12312313">words</label>
    # </div>
    # '''






    # sentence += '''
    #     <form>
    #         <div class="form-row align-items-center">
    #             <div class="col-4">
    #                 <label class="mr-sm-2" for="inlineFormCustomSelect">123</label>
    #                 <select class="custom-select mr-sm-0" id="inlineFormCustomSelect" style="font-size:7px;">
    #                     <option selected value="名詞" style="font-size:7px;">Choose...</option>
    #                     <option value="名詞" style="font-size:7px;">名詞</option>
    #                     <option value="動詞" style="font-size:7px;">動詞</option>
    #                 </select>

    #                 <select id="select_words" name="town" style="font-size:12px;">
    #                     <option value="名詞">名詞</option>
    #                     <option value="動詞">動詞</option>
    #                 </select>
    #             </div>
            
     
    #         </div>
    #     </form>
    # '''


    context = {
        'course':course,
        'lessons':lessons,
        'Sentence':sentence
        }
    # print(context)
    
    return render(request, 'course/Sentence.html', context)


def Sentence(request,lessonId):
    '''
    顯示lessonRead
    '''
    # 無單字版本
    lesson = get_object_or_404(Lesson, id=lessonId)
    words = Words.objects.filter(lesson=lesson)


    example = []
    example_json ={}
    for word in words:
        example.append(word.example)
        example_json.update({word:word.example})
    print(example)
    print(example_json)


    # ['One of the best known of Aesop\'s fables is "The Lion and the Mouse."', 'The moral of "The Lion and the Mouse" is: Little friends may prove to be great friends.']
    
    

    '''
        判斷詞性部分
    '''
    from textblob import TextBlob

    text = example[0]

    '''
        google翻譯
    '''
    # from py_translator import TEXTLIB

    # s = TEXTLIB().translator(is_html=False, text= example[0] , lang_to='zh-TW', proxy=False)

    s = translator.translate(example[0], dest='zh-tw',src='en')

    # print(s)
    example_tw = s.text


    blob = TextBlob(text)
    # print(blob.tags)           
    # [('The', 'DT'), ('titular', 'JJ'),
    #  ('threat', 'NN'), ('of', 'IN'), ...]
    
    words_tag_2_tw={

        'CC':'並列連詞',
        'CD':'純數,基數',
        'DT':'限定詞(置於名詞前起限定作用,如 the、some、my 等)',
        'EX':'存在句,存現句',
        'FW':'外來語',
        'IN':'介詞/從屬連詞,主從連詞,從屬連接詞',
        'JJ':'形容詞',
        'JJR':'（形容詞或副詞的）比較級形式',
        'JJS':'（形容詞或副詞的）最高級',
        'LS':'listmarker',
        'MD':'形態的，形式的 , 語氣的；情態的',
        'NN':'名詞單數形式',
        'NNS':'名詞複數形式',
        'NNP':'專有名詞',
        'NNPS':'專有名詞複數形式',
        'PDT':"前位限定詞",
        'POS':'屬有詞,結束語',
        'PRP':'人稱代詞',
        'PRP$':'物主代詞',
        'RB':'副詞',
        'RBR':'（形容詞或副詞的）比較級形式',
        'RBS':'（形容詞或副詞的）最高級',
        'RP':'小品詞(與動詞構成短語動詞的副詞或介詞)',
        'TO':'to',
        'UH':'感嘆詞；感嘆語',
        'VB':'動詞',
        'VBD':'動詞,過去時,過去式',
        'VBG':'動詞 ,動名詞/現在分詞',
        'VBN':'動詞,過去分詞',
        'VBP':'動詞,現在',
        'VBZ':'動詞,第三人稱',
        'WDT':'限定詞（置於名詞前起限定作用，如 the、some、my 等）',
        'WP':'代詞（代替名詞或名詞詞組的單詞）',
        'WP$':'所有格；屬有詞',
        'WRB':'副詞'
    }

    sentence = ''

    sentence += '''
        <div class="row"> 
    '''
  
    for word,tag in  blob.tags:
        if word == "'s":
            sentence += '<font  data-toggle="tooltip" data-html="true" title="'+words_tag_2_tw[tag]+'">'+word+'</font>'
        else:
            sentence += '<font  data-toggle="tooltip" data-html="true" title="'+words_tag_2_tw[tag]+'">&nbsp;'+word+'</font>'

    sentence += '''   
        </div>
        <div class="row"> 
            '''+example_tw+'''
        </div>
    '''
    
    
    from stat_parser import Parser, display_tree
    """
    svg
    """
    parser = Parser()

    tree = parser.parse("Jane's problem with her parents is a classic example of bad communicationa")

    setting_trees = tree.productions()
  
    # print(tree)
    # (SBAR+S
    #   (NP (PRP I))
    #   (VP
    #     (VBN shot)
    #     (NP (DT an) (NN elephant))
    #     (PP (IN in) (NP (PRP$ my) (NN pajamas)))))

    # print(setting_trees)
    # [SBAR+S -> NP VP, NP -> PRP, PRP -> 'I', VP -> VBN NP PP, VBN -> 'shot', NP -> DT NN, DT -> 'an', NN -> 'elephant', PP -> IN NP, IN -> 'in', NP -> PRP$ NN, PRP$ -> 'my', NN -> 'pajamas']

    # tree.draw()

    # for setting_tree in setting_trees:
    #     print(setting_tree)
        
    # SBAR+S -> NP VP
    # NP -> PRP
    # PRP -> 'I'
    # VP -> VBN NP PP
    # VBN -> 'shot'
    # NP -> DT NN
    # DT -> 'an'
    # NN -> 'elephant'
    # PP -> IN NP
    # IN -> 'in'
    # NP -> PRP$ NN
    # PRP$ -> 'my'
    # NN -> 'pajamas'

    import svgling
    tree_svg = svgling.draw_tree(tree,leaf_nodes_align=True)
    tree_svg = tree_svg.get_svg().tostring()
    svg_head='<svg baseProfile="full" height="100%" width="100%" '
    tree_svg = svg_head + tree_svg[tree_svg.find("preserveAspectRatio"):]
    # print(tree_svg)

    context = {
        'lesson':lesson,
        'Sentence':sentence,
        'words': words,
        'tree': tree_svg
        }

    return render(request, 'course/Sentence.html', context)


def WordRead(request,WordsId):
    '''
    顯示WordRead
    '''
    # 無單字版本
    # lesson = get_object_or_404(Lesson, id=lessonId)
    # words = Words.objects.filter(lesson=lesson)
    words = get_object_or_404(Words, id=WordsId)

    from thesaurus import Word
    import nltk

    text = words.example
    
    if  words.example_svg == None :
        '''如果資料庫沒有example_svg資料 則產生例句詞性結構樹'''
        print('資料庫沒有example_svg資料')
        from stat_parser import Parser, display_tree
        """
        svg
        """

        
        parser = Parser()
        tree = parser.parse(text)
        setting_trees = tree.productions()

        import svgling

        tree_svg = svgling.draw_tree(tree,leaf_nodes_align=True)
        tree_svg = tree_svg.get_svg().tostring()
        svg_head='<svg baseProfile="full" height="100%" width="100%" '
        tree_svg = svg_head + tree_svg[tree_svg.find("preserveAspectRatio"):]
        example_svg_data = {
            'example_svg':tree_svg
        }
        Words.objects.filter(id=WordsId).update(**example_svg_data)
    else:
        '''如果已有例句詞性結構樹則只取出顯示'''
        tree_svg = words.example_svg


    
    # Words.objects.filter(id=WordsId).update(**data)

    # print(tree_svg)
    # svgling.draw_tree(tree,leaf_nodes_align=True)


    '''
        判斷詞性部分
    '''
    # from textblob import TextBlob

    # blob = TextBlob(text)        

    words_tag_2_tw={
        'CC':'並列連詞',
        'CD':'純數,基數',
        'DT':'限定詞(置於名詞前起限定作用,如 the、some、my 等)',
        'EX':'存在句,存現句',
        'FW':'外來語',
        'IN':'介詞/從屬連詞,主從連詞,從屬連接詞',
        'JJ':'形容詞',
        'JJR':'（形容詞或副詞的）比較級形式',
        'JJS':'（形容詞或副詞的）最高級',
        'LS':'listmarker',
        'MD':'形態的，形式的 , 語氣的；情態的',
        'NN':'名詞單數形式',
        'NNS':'名詞複數形式',
        'NNP':'專有名詞',
        'NNPS':'專有名詞複數形式',
        'PDT':"前位限定詞",
        'POS':'屬有詞,結束語',
        'PRP':'人稱代詞',
        'PRP$':'物主代詞',
        'RB':'副詞',
        'RBR':'（形容詞或副詞的）比較級形式',
        'RBS':'（形容詞或副詞的）最高級',
        'RP':'小品詞(與動詞構成短語動詞的副詞或介詞)',
        'TO':'to',
        'UH':'感嘆詞；感嘆語',
        'VB':'動詞',
        'VBD':'動詞,過去時,過去式',
        'VBG':'動詞 ,動名詞/現在分詞',
        'VBN':'動詞,過去分詞',
        'VBP':'動詞,現在',
        'VBZ':'動詞,第三人稱',
        'WDT':'限定詞（置於名詞前起限定作用，如 the、some、my 等）',
        'WP':'代詞（代替名詞或名詞詞組的單詞）',
        'WP$':'所有格；屬有詞',
        'WRB':'副詞'
    }

    output_words = []
    output_tags = []

    import nltk
    nltk_words = nltk.word_tokenize(text)

    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%' ,'"','``',"''"]
    text_list = [word for word in nltk_words if word not in english_punctuations]
    word_tag = nltk.pos_tag(text_list)

    # synonyms = [[], ["about", "appertaining to", "appropriate to", "as concerns", "as regards", "attributed to", "away from", "based on", "belonging to", "characterized by", "coming from", "concerning", "connected with", "consisting of", "containing", "epithetical", "going from", "in reference to", "in regard to", "like", "made from", "out from", "out of", "peculiar to", "pertaining to", "proceeding from", "referring to", "regarding", "related to", "showing", "about", "concerning", "from", "like", "regarding"], ["affecting", "breathtaking", "climactic", "comic", "dramaturgic", "dramaturgical", "effective", "electrifying", "emotional", "expressive", "farcical", "histrionic", "impressive", "melodramatic", "powerful", "sensational", "spectacular", "startling", "striking", "sudden", "suspenseful", "tense"], ["bad", "finest", "first", "first-rate", "leading", "outstanding", "perfect", "terrific", "tough"], [], ["about", "appertaining to", "appropriate to", "as concerns", "as regards", "attributed to", "away from", "based on", "belonging to", "characterized by", "coming from", "concerning", "connected with", "consisting of", "containing", "epithetical", "going from", "in reference to", "in regard to", "like", "made from", "out from", "out of", "peculiar to", "pertaining to", "proceeding from", "referring to", "regarding", "related to", "showing", "about", "concerning", "from", "like", "regarding"], [], [], ["fantasy", "fiction", "legend", "myth", "parable", "tale", "yarn"], ["abide", "act", "breathe", "continue", "do", "endure", "hold", "inhabit", "last", "live", "move", "obtain", "persist", "prevail", "remain", "rest", "stand", "stay", "subsist", "survive", "transpire", "befall", "occur"], [], ["affecting", "breathtaking", "climactic", "comic", "dramaturgic", "dramaturgical", "effective", "electrifying", "emotional", "expressive", "farcical", "histrionic", "impressive", "melodramatic", "powerful", "sensational", "spectacular", "startling", "striking", "sudden", "suspenseful", "tense"], [], ["along with", "also", "as a consequence", "as well as", "furthermore", "including", "moreover", "together with"], ["affecting", "breathtaking", "climactic", "comic", "dramaturgic", "dramaturgical", "effective", "electrifying", "emotional", "expressive", "farcical", "histrionic", "impressive", "melodramatic", "powerful", "sensational", "spectacular", "startling", "striking", "sudden", "suspenseful", "tense"], []]
    
    #=============#=============#=============#=============#=============#=============#=============#=============#=============
    
    '''
    產生句子 ajax
    '''
    # from thesaurus import Word
    # import nltk

    # text = "One of the best known of Aesop's fables is “The Lion and the Mouse"

    words_tag_2_ez={
        'CC':'conj',
        'CD':'純數,基數',
        'DT':'adj',
        'EX':'存在句,存現句',
        'FW':'外來語',
        'IN':'prep',
        'JJ':'adj',
        'JJR':'adj',
        'JJS':'adj',
        'LS':'listmarker',
        'MD':'形態的，形式的 , 語氣的；情態的',
        'NN':'noun',
        'NNS':'noun',
        'NNP':'專有名詞',
        'NNPS':'專有名詞複數形式',
        'PDT':"前位限定詞",
        'POS':'屬有詞,結束語',
        'PRP':'人稱代詞',
        'PRP$':'物主代詞',
        'RB':'adv',
        'RBR':'（形容詞或副詞的）比較級形式',
        'RBS':'（形容詞或副詞的）最高級',
        'RP':'小品詞(與動詞構成短語動詞的副詞或介詞)',
        'TO':'to',
        'UH':'interj',
        'VB':'verb',
        'VBD':'verb',
        'VBG':'verb',
        'VBN':'verb',
        'VBP':'verb',
        'VBZ':'verb',
        'WDT':'限定詞（置於名詞前起限定作用，如 the、some、my 等）',
        'WP':'pron',
        'WP$':'所有格；屬有詞',
        'WRB':'副詞'
    }

    # from textblob import TextBlob
    # blob = TextBlob(text)
    # for word,tag in  blob.tags:
    #     print(word,tag,words_tag_2_tw[tag])

    def replace_word(input_text,tag):
        try: 
            w = Word(input_text)
            output=[]
            # 之後要改成第一個優先
        #     tag = "adj"
            setting_ranks = [3]
            setting_rank = 3
            i = 0    
            words_count=0
            output_words = []
            ws_len = len(w.synonyms('all'))

            while (i < ws_len):
            #     print(i)
            #     print(w.synonyms('all',relevance=setting_ranks,partOfSpeech=tag)[i])

                w_len = len(w.synonyms('all',relevance=setting_ranks,partOfSpeech=tag)[i])

                if(w_len < 1): #如果沒有元素在 
                    i+=1
            #         print("沒有元素在")
                    continue

                words_count+=w_len

            #     print(w_len,words_count)

                if (words_count < 4 and words_count > 0 ): #如果太少 減少rank並重新迴圈
                    setting_rank -=1 
                    setting_ranks.append(setting_rank)
                    i = 0
            #         print("迴圈重新")
                    output_words=[]
                    continue

                output_words.append(w.synonyms('all',relevance=setting_ranks,partOfSpeech=tag)[i][1:])

                i+=1

            output_words = [j for sub in output_words for j in sub] #多緯轉單維

            return output_words
        except:
            return (-1)

    # w.synonyms('all',relevance=3)

    # replace_word_lists=[]
    # for word,tag in blob.tags:
    # #     print(word,tag)
    #     tmp = replace_word(word,words_tag_2_ez[tag])
    #     # print(word,words_tag_2_ez[tag])

    #     if (tmp != -1):
    #         # print(tmp)
    #         replace_word_lists.append(tmp)
    #         pass
    #     else:
    #         replace_word_lists.append([])
    #         pass
    
    #=============#=============#=============#=============#=============#=============#=============#=============#=============#=============#=============
    
    
    for word,pos in word_tag:
        # print(word,pos)
        output_words.append(str(word))
        output_tags.append(words_tag_2_tw[pos])

        #==#==#==#==#==#==#==#==#==#==#==#==#==#==#==

        # tmp = replace_word(word,words_tag_2_ez[pos])
        # if (tmp != -1):
        #     # print(tmp)
        #     replace_word_lists.append(tmp)
        #     pass
        # else:
        #     replace_word_lists.append([])
        #     pass

    # replace_word_lists = [[], ["about", "appertaining to", "appropriate to", "as concerns", "as regards", "attributed to", "away from", "based on", "belonging to", "characterized by", "coming from", "concerning", "connected with", "consisting of", "containing", "epithetical", "going from", "in reference to", "in regard to", "like", "made from", "out from", "out of", "peculiar to", "pertaining to", "proceeding from", "referring to", "regarding", "related to", "showing", "about", "concerning", "from", "like", "regarding"], ["affecting", "breathtaking", "climactic", "comic", "dramaturgic", "dramaturgical", "effective", "electrifying", "emotional", "expressive", "farcical", "histrionic", "impressive", "melodramatic", "powerful", "sensational", "spectacular", "startling", "striking", "sudden", "suspenseful", "tense"], ["bad", "finest", "first", "first-rate", "leading", "outstanding", "perfect", "terrific", "tough"], [], ["about", "appertaining to", "appropriate to", "as concerns", "as regards", "attributed to", "away from", "based on", "belonging to", "characterized by", "coming from", "concerning", "connected with", "consisting of", "containing", "epithetical", "going from", "in reference to", "in regard to", "like", "made from", "out from", "out of", "peculiar to", "pertaining to", "proceeding from", "referring to", "regarding", "related to", "showing", "about", "concerning", "from", "like", "regarding"], [], [], ["fantasy", "fiction", "legend", "myth", "parable", "tale", "yarn"], ["abide", "act", "breathe", "continue", "do", "endure", "hold", "inhabit", "last", "live", "move", "obtain", "persist", "prevail", "remain", "rest", "stand", "stay", "subsist", "survive", "transpire", "befall", "occur"], [], ["affecting", "breathtaking", "climactic", "comic", "dramaturgic", "dramaturgical", "effective", "electrifying", "emotional", "expressive", "farcical", "histrionic", "impressive", "melodramatic", "powerful", "sensational", "spectacular", "startling", "striking", "sudden", "suspenseful", "tense"], [], ["along with", "also", "as a consequence", "as well as", "furthermore", "including", "moreover", "together with"], ["affecting", "breathtaking", "climactic", "comic", "dramaturgic", "dramaturgical", "effective", "electrifying", "emotional", "expressive", "farcical", "histrionic", "impressive", "melodramatic", "powerful", "sensational", "spectacular", "startling", "striking", "sudden", "suspenseful", "tense"], []]
    # replace_word_lists = [replace_word_lists]

    # for word,tag in blob.tags:
        # output_words.update({word:words_tag_2_tw[tag]})
        # output_words.append(word)
        # output_tags.append(words_tag_2_tw[tag])
    

    html_output_sentence_text = []
    output_html=[]
    for i in range(0,len(output_words)):
        html_output = ""
        for j in range(0,len(output_words)):
            if (i != j):
                html_output += output_words[j] +" "
            if (i == j ):
                html_output += '<font color="red"><b>'+ output_words[i] +'</b></font> '
        html_output +=" "
        html_output_sentence_text.append(html_output)
        #==#==#==#==#==#==#==#==#==#==#==#==#==#==#==

        tmp = replace_word(word_tag[i][0],words_tag_2_ez[word_tag[i][1]])

        if (tmp != -1):
            # print(tmp)
            output_html+=[(output_words[i],words_tag_2_tw[word_tag[i][1]],html_output,tmp)]
        else:
            output_html+=[(output_words[i],words_tag_2_tw[word_tag[i][1]],html_output,[])]

        #==#==#==#==#==#==#==#==#==#==#==#==#==#==#==

        # output_html+=[(output_words[i],words_tag_2_tw[word_tag[i][1]],html_output)]

        # print(output_words[i],output_tags[i],synonyms[i])

    # print(html_output_sentence_text)

    # output_html=[output_words,html_output_sentence_text]


    context = {
        'words': words,
        'tree_svg':tree_svg,
        'output_words':list(output_words),
        'output_tags':list(output_tags),
        'range':list(range(0,len(output_words))),
        'html_output_sentence_text':html_output_sentence_text,
        'output_html':list(output_html)
        }

    return render(request, 'course/words.html', context)


def synonym_save_tree_svg(request): #未實作
    '''
    透過ajax 傳來要儲存句子詞性結構樹
    '''
    word_id = request.GET.get('word_id')
    

    if (word_id == None or word_id ==''):

        return JsonResponse('error', safe=False)

    else:
        # print(syn_ck_json)
        import json
        words = get_object_or_404(Words, id=word_id)

        from thesaurus import Word
        import nltk
        from stat_parser import Parser, display_tree
        """
        svg
        """
        text = words.example
        parser = Parser()
        tree = parser.parse(text)
        setting_trees = tree.productions()

        import svgling

        tree_svg = svgling.draw_tree(tree,leaf_nodes_align=True)
        tree_svg = tree_svg.get_svg().tostring()
        svg_head='<svg baseProfile="full" height="100%" width="100%" '
        tree_svg = svg_head + tree_svg[tree_svg.find("preserveAspectRatio"):]


        
        data = {
            'example_svg':tree_svg
        }

        Words.objects.filter(id=word_id).update(**data)

        return JsonResponse('ok', safe=False)


def translator_Example(request):
    '''
    翻譯句子 ajax
    '''
    # from py_translator import TEXTLIB

    example = request.GET.get('text')
    print(example)
    if (example == None or example ==''):
        return JsonResponse('請確保例句英文無錯誤', safe=False)
    else:
        # example_tw = TEXTLIB().translator(is_html=False, text=example , lang_to='zh-TW', proxy=False)
        example_tw = translator.translate(example, dest='zh-tw',src='en')
        print(example_tw.text)
        return JsonResponse(example_tw.text, safe=False)



word_example_generator={}
word_example_generator_input_word = ''
import time
def word_example_generator_fun(request):
    '''
    產生句子 ajax
    '''
    input_word = request.GET.get('word')
    print(input_word)
    
    if (input_word == None or input_word ==''):

        return JsonResponse('無法產生例句', safe=False)
    else:
        if input_word.isalpha():
            global word_example_generator
            global word_example_generator_input_word
            new_example_sentence_generator=''
            timer_f=0

            if input_word == word_example_generator_input_word:
                while ( len(new_example_sentence_generator) >120) and timer_f<10:
                    time.sleep(1)
                    timer_f = timer_f +1
                    new_example_sentence_generator = example_sentence_generator(word_example_generator)
                    print("!!!time!!!!",len(new_example_sentence_generator),timer_f)
                timer_f = 0
                return JsonResponse(example_sentence_generator(word_example_generator), safe=False)
            else:

                word_example_generator = example_generator(input_word)
                word_example_generator_input_word=input_word
                new_example_sentence_generator = example_sentence_generator(word_example_generator)
                while ( len(new_example_sentence_generator) >120) and timer_f<10:
                    time.sleep(1)
                    timer_f = timer_f +1
                    new_example_sentence_generator = example_sentence_generator(word_example_generator)
                    print("!!!time!!!!",len(new_example_sentence_generator),timer_f)
                timer_f = 0
                # return JsonResponse(example_sentence_generator(word_example_generator), safe=False)
                return JsonResponse(new_example_sentence_generator, safe=False)

        else:
            return JsonResponse('無法產生例句', safe=False)




    # import requests
    # from bs4 import BeautifulSoup

    # def Crawler_cha(keyword = 'fable'):
        
    #     headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    #     }
    #     rs = requests.Session()
    #     url = "https://tw.ichacha.net/hy/zaoju.aspx?q="+keyword
    #     res = rs.get(url, headers=headers)
    #     bs = BeautifulSoup(res.text,'lxml')
        
    #     examples=[]

    #     raw_pages = bs.find_all('a', attrs={'style':'text-decoration:underline;color:green'})
    #     pages=[]

    #     if raw_pages:
    #         print("還有例句")

    #         for page in raw_pages:
    #     #         print(page.get('href'))
    #             pages.append(page.get('href'))


    #             raw_examples = bs.find_all('li', attrs={'style':'text-align:left'})
    #             for raw_example in raw_examples:
    #     #             print(raw_example.text)
    #                 examples.append(raw_example.text)


    #             url = "https://tw.ichacha.net"+page.get('href')
    #             res = rs.get(url, headers=headers)
    #             bs = BeautifulSoup(res.text,'lxml')

    #     else:
    #         print("沒有更多例句了")
        
    #     return examples



    # # Crawler_cha('moral')


    # lesson = get_object_or_404(Lesson, id=1)
    # words = Words.objects.filter(lesson=lesson)
    # examples = Examples.objects.filter(words=words)


    # for word in words:
    #     print(word)
    #     examples_craw = Crawler_cha(str(word))
    #     print(examples_craw)
    #     for example_craw in examples_craw:
    #         examples = Examples.objects.create(words=word,examples=example_craw)



        # word = get_object_or_404(Course, id=courseId)
        # lessons = {}
        # example = []
        # for lesson in Lesson.objects.all():
        #     # print(Words.objects.filter(lesson=lesson))
        #     a = Words.objects.filter(lesson=lesson)
        #     for e in a:
        #         # print(e.example)
        #         example.append(e.example)
        #     lessons.update({lesson:Words.objects.filter(lesson=lesson)})
            
  

    # print(context)





def word_example_generator_new(request):
    '''
    產生句子 ajax
    '''
    input_word = request.GET.get('word')
    print(input_word)
    words = Words.objects.filter(words=input_word)
    print(words)
    
    examples = Examples.objects.filter(words=words[0].id)
    print(examples)
    for example in examples:
        print(example.examples)
    
    import random
    print(len(examples))
    return JsonResponse(examples[random.randint(0,len(examples))].examples, safe=False)
    # if (input_word == None or input_word ==''):

    #     return JsonResponse('無法產生例句', safe=False)
    # else:
    #     if input_word.isalpha():
            
    #         return JsonResponse(new_example_sentence_generator, safe=False)

    #     else:
    return JsonResponse('無法產生例句', safe=False)







def wordUpdate(request, WordsId):
    '''
    更新單字
    '''
    # word = get_object_or_404(Words, id=WordsId)
    template = 'course/courseUpdate.html'


    if request.method == 'GET':
        return redirect('/')

    # POST
    if request.method == 'POST':
        word_ = request.POST.get('word', None)
        kk_ = request.POST.get('kk', None)
        subject_ = request.POST.get('subject', None)
        chinese_ = request.POST.get('chinese', None)
        description_ = request.POST.get('description', None)
        example_ = request.POST.get('example', None)
        example_tw_ = request.POST.get('example_tw', None)

        # word = Words.objects.get(id=WordsId)
        # word.word=word_
        # word.kk=kk_
        # word.subject=subject_
        # word.chinese=chinese_
        # word.description=description_
        # word.example=example_
        # word.example_tw=example_tw_
        # word.save()

        data = {
            'words':word_,
            'kk':kk_,
            'subject':subject_,
            'chinese':chinese_,
            'description':description_,
            'example':example_,
            'example_tw':example_tw_
            }

        Words.objects.filter(id=WordsId).update(**data)
        path_ = '/dashboard/WordRead/'+str(WordsId)+'/'

        return redirect(path_)


def synonyms(request):
    '''
    產生句子 ajax
    '''
    from thesaurus import Word
    import nltk

    text = "One of the best known of Aesop's fables is “The Lion and the Mouse"

    words_tag_2_tw={
        'CC':'並列連詞',
        'CD':'純數,基數',
        'DT':'限定詞(置於名詞前起限定作用,如 the、some、my 等)',
        'EX':'存在句,存現句',
        'FW':'外來語',
        'IN':'介詞/從屬連詞,主從連詞,從屬連接詞',
        'JJ':'形容詞',
        'JJR':'（形容詞或副詞的）比較級形式',
        'JJS':'（形容詞或副詞的）最高級',
        'LS':'listmarker',
        'MD':'形態的，形式的 , 語氣的；情態的',
        'NN':'名詞單數形式',
        'NNS':'名詞複數形式',
        'NNP':'專有名詞',
        'NNPS':'專有名詞複數形式',
        'PDT':"前位限定詞",
        'POS':'屬有詞,結束語',
        'PRP':'人稱代詞',
        'PRP$':'物主代詞',
        'RB':'副詞',
        'RBR':'（形容詞或副詞的）比較級形式',
        'RBS':'（形容詞或副詞的）最高級',
        'RP':'小品詞(與動詞構成短語動詞的副詞或介詞)',
        'TO':'to',
        'UH':'感嘆詞；感嘆語',
        'VB':'動詞',
        'VBD':'動詞,過去時,過去式',
        'VBG':'動詞 ,動名詞/現在分詞',
        'VBN':'動詞,過去分詞',
        'VBP':'動詞,現在',
        'VBZ':'動詞,第三人稱',
        'WDT':'限定詞（置於名詞前起限定作用，如 the、some、my 等）',
        'WP':'代詞（代替名詞或名詞詞組的單詞）',
        'WP$':'所有格；屬有詞',
        'WRB':'副詞'
    }

    words_tag_2_ez={
        'CC':'conj',
        'CD':'純數,基數',
        'DT':'adj',
        'EX':'存在句,存現句',
        'FW':'外來語',
        'IN':'prep',
        'JJ':'adj',
        'JJR':'adj',
        'JJS':'adj',
        'LS':'listmarker',
        'MD':'形態的，形式的 , 語氣的；情態的',
        'NN':'noun',
        'NNS':'noun',
        'NNP':'專有名詞',
        'NNPS':'專有名詞複數形式',
        'PDT':"前位限定詞",
        'POS':'屬有詞,結束語',
        'PRP':'人稱代詞',
        'PRP$':'物主代詞',
        'RB':'adv',
        'RBR':'（形容詞或副詞的）比較級形式',
        'RBS':'（形容詞或副詞的）最高級',
        'RP':'小品詞(與動詞構成短語動詞的副詞或介詞)',
        'TO':'to',
        'UH':'interj',
        'VB':'verb',
        'VBD':'verb',
        'VBG':'verb',
        'VBN':'verb',
        'VBP':'verb',
        'VBZ':'verb',
        'WDT':'限定詞（置於名詞前起限定作用，如 the、some、my 等）',
        'WP':'pron',
        'WP$':'所有格；屬有詞',
        'WRB':'副詞'
    }

    from textblob import TextBlob
    blob = TextBlob(text)
    # for word,tag in  blob.tags:
    #     print(word,tag,words_tag_2_tw[tag])

    def replace_word(input_text,tag):
        try: 
            w = Word(input_text)
            output=[]
            # 之後要改成第一個優先
        #     tag = "adj"
            setting_ranks = [3]
            setting_rank = 3
            i = 0    
            words_count=0
            output_words = []
            ws_len = len(w.synonyms('all'))

            while (i < ws_len):
            #     print(i)
            #     print(w.synonyms('all',relevance=setting_ranks,partOfSpeech=tag)[i])

                w_len = len(w.synonyms('all',relevance=setting_ranks,partOfSpeech=tag)[i])

                if(w_len < 1): #如果沒有元素在 
                    i+=1
            #         print("沒有元素在")
                    continue

                words_count+=w_len

            #     print(w_len,words_count)

                if (words_count < 4 and words_count > 0 ): #如果太少 減少rank並重新迴圈
                    setting_rank -=1 
                    setting_ranks.append(setting_rank)
                    i = 0
            #         print("迴圈重新")
                    output_words=[]
                    continue

                output_words.append(w.synonyms('all',relevance=setting_ranks,partOfSpeech=tag)[i][1:])

                i+=1

            output_words = [j for sub in output_words for j in sub] #多緯轉單維

            return output_words
        except:
            return (-1)

    # w.synonyms('all',relevance=3)

    replace_word_lists=[]
    for word,tag in blob.tags:
    #     print(word,tag)
        tmp = replace_word(word,words_tag_2_ez[tag])
        # print(word,words_tag_2_ez[tag])

        if (tmp != -1):
            # print(tmp)
            replace_word_lists.append(tmp)
            pass
        else:
            replace_word_lists.append([])
            pass

    return JsonResponse(list(replace_word_lists), safe=False)


def synonymsave(request):
    '''
    透過ajax 傳來要儲存的單字id和替換字json
    '''
    word_id = request.GET.get('word_id')
    syn_ck_json = request.GET.get('syn_ck_json')

    if (word_id == None or word_id ==''  or syn_ck_json == None or syn_ck_json =='' ):

        return JsonResponse('error', safe=False)

    else:
        # print(syn_ck_json)
        import json
        words = get_object_or_404(Words, id=word_id)
        syn_ck_json = (syn_ck_json)
        data = {
            'example_json':syn_ck_json
        }

        Words.objects.filter(id=word_id).update(**data)

        return JsonResponse('ok', safe=False)


def synonymsMK(request):
    '''
    透過ajax 隨機產生一組句子
    '''
    word_id = request.GET.get('word_id')
    words = get_object_or_404(Words, id=word_id)



    if (word_id == None or word_id ==''):
        return JsonResponse("單字錯誤", safe=False)
    
    # print(words.example_json)
    import json
    # json.loads

    if(words.example_json == None or words.example_json ==''):
        return JsonResponse("尚無資料，請先確認例句產生設定", safe=False)

    db_syn_json = json.loads(words.example_json)
    
    # db_list2='[[],["about","appertaining to","appropriate to","as concerns","as regards","attributed to","away from"],["affecting","breathtaking","climactic"],["bad","finest","first"],[],["about","appertaining to","appropriate to","as concerns"],[]]'
    # j = json.loads(words.example_json)

    # print(db_syn_json[2][0])
    # print(len(db_syn_json))
    example = words.example

    import random

    # print (random.randint(1,50))
    
    import nltk
    nltk_words = nltk.word_tokenize(example)

    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%' ,'"','``',"''"]
    text_list = [word for word in nltk_words if word not in english_punctuations]
    word_tag = nltk.pos_tag(text_list)

    output_words = []
    # output_tags = []
    output_text = ""


    for word,pos in word_tag:
        # print(word,pos)
        output_words.append(str(word))
        # output_tags.append(words_tag_2_tw[pos])

    for i in range(0,len(db_syn_json)):

        # print(len(db_syn_json[i]))
        if (len(db_syn_json[i]) == 0):
            output_text += (output_words[i])+" "
        elif (len(db_syn_json[i]) > 0):
            output_text += (db_syn_json[i][random.randint(0,len(db_syn_json[i]))-1]) +" "

        # pass
    # print(output_text)



    return JsonResponse(output_text, safe=False)


def ajax_index(request):
    return render(request, 'course/ajax_test.html')


def ajax_list(request):
    print(request.GET.get('text'))
    a = range(100)
    return JsonResponse(list(a), safe=False)


def ajax_dict(request):
    is_ajax = False
    if request.is_ajax():
        is_ajax = True
    name_dict = {'twz': 'Love python and Django',
                 'zqxt': 'I am teaching Django', 'is_ajax': is_ajax}
    return JsonResponse(name_dict)


def ajax_jquery(request):
    print(request.GET.getlist('b[]'))
    is_ajax = False
    if request.is_ajax():
        is_ajax = True
    test = {'GET': 'GET',
            'array': [1, 2, 3, 4],
            'a': request.GET['a'],
            'b[]': request.GET.getlist('b[]'),
            'is_ajax': is_ajax,
            }
    return JsonResponse(test)


# @csrf_exempt #忽略 csrf
def ajax_jquery_POST(request):
    print(request.POST.getlist('b[]'))
    is_ajax = False
    if request.is_ajax():
        is_ajax = True
    test = {'POST': 'POST',
            'array': [1, 2, 3, 4],
            'a': request.POST['a'],
            'b[]': request.POST.getlist('b[]'),
            'is_ajax': is_ajax,
            }
    return JsonResponse(test)


# @csrf_exempt #忽略 csrf
def ajax_jquery_sample(request):
    print(request.POST.getlist('b[]'))
    is_ajax = False
    if request.is_ajax():
        is_ajax = True
    test = {'POST': 'POST',
            'array': [1, 2, 3, 4],
            'a': request.POST['a'],
            'b[]': request.POST.getlist('b[]'),
            'is_ajax': is_ajax,
            }
    return JsonResponse(test)