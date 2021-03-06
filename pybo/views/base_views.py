from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404
import logging
from pybo.models import Question, Answer

logger = logging.getLogger('pybo')


def index(request):
    logger.info("output to INFO level")
    # input parameter
    page = request.GET.get('page', '1')  # page
    kw = request.GET.get('kw', '')  # keyword
    so = request.GET.get('so', 'recent')  # sorting criteria

    if so == 'recommend':
        question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:
        question_list = Question.objects.order_by('-create_date')

    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(answer__author__username__icontains=kw)
        ).distinct()

    # page handling
    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}

    return render(request, 'pybo/question_list.html', context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    page = request.GET.get('page', '1')  # page
    so = request.GET.get('so', 'recent')  # sorting criteria

    if so == 'recommend':
        answer_list = Answer.objects.filter(question_id=question.id).annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    else:
        answer_list = Answer.objects.filter(question_id=question.id).order_by('-create_date')

    # paging handling
    paginator = Paginator(answer_list, 5)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question': question, 'answer_list': page_obj, 'so': so}
    return render(request, 'pybo/question_detail.html', context)
