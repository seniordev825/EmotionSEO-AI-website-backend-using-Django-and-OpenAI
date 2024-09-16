from rest_framework import generics,status,views,permissions
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer , UserSerializer
from .utiliz import generate_otp, send_otp_email
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import stripe 
import aiohttp 
from time import sleep  
from django.conf import settings 
from rest_framework.views import APIView  
from openai import OpenAI 
from rest_framework.permissions import IsAuthenticated, AllowAny 
import json 
from urllib.parse import urlencode
from rest_framework import serializers  
from rest_framework.response import Response 
from .mixins import PublicApiMixin, ApiErrorsMixin 
from .utils import google_get_access_token, google_get_user_info, generate_tokens_for_user
from .models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.core.mail import EmailMessage 
from xhtml2pdf import pisa 
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import HttpResponse
import smtplib  
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from django.template.loader import get_template
import os
import datetime
import requests
import json
import base64
from dotenv import load_dotenv 
load_dotenv() 
api_key = os.getenv('OPENAI_KEY')
client = OpenAI(api_key = api_key)

def generatingContentByOpenai(prompt):
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'  
            },
            {"role": "user", "content": prompt},
        ]
    )
    content = res.choices[0].message.content
    return content

def contentChecking(content):
    if content[-1]==",":                          ## This means that the last of the sentence is ",".         
      content[-1]=="."                                 
    elif content[-1]!=',' and content[-1]!='.':     ## wrong sentence               
      content=content+"."                           
    elif content[-1]=='.':                         ## correct sentence  
      content=content             
    return content
 
def functionPromptPostUrlEnglish(subject, url, emotion, language, socialType):
    prompt=f'''Write a post for {socialType} in English. The post must include the site information with {url}. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {socialType} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {emotion}.
The topic of this post should be {subject} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
    return prompt

def functionPromptPostNonUrlEnglish(subject, url, emotion, language, socialType):
    prompt=f'''Write a post for {socialType} in English. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {socialType} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {emotion}.
The topic of this post should be {subject} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
    return prompt

def functionPromptPostUrlSpanish(subject, url, emotion, language, socialType):
    prompt=f'''Escribe un post para {socialType} en Español. El post debe incluir la información del sitio con {url}. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {socialType} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {emotion}.
El tema de esta publicación debe ser {subject} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
    return prompt

def functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType):
    prompt=f'''Escribe un post para {socialType} en Español. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {socialType} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {emotion}.
El tema de esta publicación debe ser {subject} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
    return prompt

def funtionPromptArticleEnglish(title, keyword, emotion, language):
    prompt = f'''Write article in English. The article must be SEO-Optmized Content and the article must be included {keyword}
        The article must be written with {emotion}.The article should typically contain 750 words. The last sentence of article must be a meaningfull and complete sentence. The last sentence must be ended a full stop.
        The title of article must be {title} and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the article naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the article easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''
    return prompt

def funtionPromptArticleSpanish(title, keyword, emotion, language):
    prompt = f'''Escribe un artículo en español.  El artículo debe ser contenido optimizado para SEO y debe incluir {keyword}. 
         El artículo debe estar escrito con {emotion}. Normalmente, el artículo debe contener 750 palabras. La última frase del artículo debe ser una frase significativa y completa. La ultima frase debe estar completa y terminar siempre el articulo con un ".".
        El título del artículo debe ser {title} y no cambies ni agregues nada, ¡y escribe con una fuente más grande que el contenido!
        Queremos que este contenido sea altamente buscable.
        Escribe el artículo de manera natural y evita comentarios o palabras (por ejemplo: contenido optimizado para SEO) que no estén relacionados con el tema.
        No incluyas símbolos innecesarios como ---, ###, **, etc.
        Añade saltos de línea, guiones e indentaciones para hacer que el artículo sea fácil de leer y entender.
        Debes considerar distinguir con precisión entre título, contenido, párrafos, etc.
        Escribe las nuevas oraciones en nuevas filas.'''
    return prompt

 
class RegisterView(generics.GenericAPIView):            
    serializer_class = RegisterSerializer
    def post(self,request):
        user=request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = generate_otp()
        serializer.validated_data['otp'] = otp
        send_otp_email(serializer.validated_data['email'], otp)
        serializer.save()
        request.session['otp'] = otp
        user_data = serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)


class PostView(APIView):                            ## APIView for social media post
    def get(self, request):
     user = request.user
     user=User.objects.get(pk=user.id)      
     if user.email=="miriamlaof@gmail.com":          ## in case of the site's owner
            subject = request.GET.get('subject')
            url = request.GET.get('url')
            emotion= request.GET.get('checkedValues')
            language= request.GET.get('language')
            socialType = request.GET.get('post')           
            promptPostUrlEnglish = functionPromptPostUrlEnglish(subject, url, emotion, language, socialType)
            promptPostNonUrlEnglish = functionPromptPostNonUrlEnglish(subject, url, emotion, language, socialType)
            promptPostUrlSpanish = functionPromptPostUrlSpanish(subject, url, emotion, language, socialType)
            promptPostNonUrlSpanish = functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType)
            if language=="English":
             if url!="":
              prompt = promptPostUrlEnglish
             elif url=="":
              prompt = promptPostNonUrlEnglish             
              generatedPost = generatingContentByOpenai(prompt)           
              content=contentChecking(generatedPost)
              return Response({"message": content}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             if url!="":
                  prompt = promptPostUrlSpanish
             elif url=="":
                prompt= promptPostNonUrlSpanish             
             generatedPost = generatingContentByOpenai(prompt)
             content=contentChecking(generatedPost)
             return Response({"message": content}, status=status.HTTP_200_OK)            
             

     elif user.email!="miriamlaof@gmail.com":     ## In case of the person that is not site's owner
        if user.usage_count < 3:                  ## Users can use this service 3 times free     
            user.usage_count += 1
            user.save()
            subject = request.GET.get('subject')
            url = request.GET.get('url')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            socialType=request.GET.get('post')
            promptPostUrlEnglish = functionPromptPostUrlEnglish(subject, url, emotion, language, socialType)
            promptPostNonUrlEnglish = functionPromptPostNonUrlEnglish(subject, url, emotion, language, socialType)
            promptPostUrlSpanish = functionPromptPostUrlSpanish(subject, url, emotion, language, socialType)
            promptPostNonUrlSpanish = functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType)
            if language=="English":
             if url!="":
                prompt= promptPostUrlEnglish
             elif url=="":
                prompt = promptPostNonUrlEnglish            
             generatedPost =generatingContentByOpenai(prompt)
             content=contentChecking(generatedPost)                
             return Response({"message": content}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             if url!="":
                prompt =  functionPromptPostUrlSpanish(subject, url, emotion, language, socialType)
             elif key2=="":
                prompt =  functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType)             
             content = generatingContentByOpenai(prompt)
             return Response({"message": content}, status=status.HTTP_200_OK)
        elif user.usage_count >=3 and (user.subscribed==False and user.word_limit==0 ):
             return Response({"message": "free"}, status=status.HTTP_201_CREATED)
        elif user.usage_count >=3 and (user.subscribed==True and user.word_number<user.word_limit):
            subject = request.GET.get('subject')
            url = request.GET.get('url')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            socialType=request.GET.get('post')
            promptPostUrlEnglish = functionPromptPostUrlEnglish(subject, url, emotion, language, socialType)
            promptPostNonUrlEnglish = functionPromptPostNonUrlEnglish(subject, url, emotion, language, socialType)
            promptPostUrlSpanish = functionPromptPostUrlSpanish(subject, url, emotion, language, socialType)
            promptPostNonUrlSpanish = functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType)
            if language=="English":
             if url!="":
                prompt = promptPostUrlEnglish
             elif url=="":
                prompt = promptPostNonUrlEnglish              
             generatedPost = generatingContentByOpenai(prompt)
             if generatedPost[-1]==",":                 
               generatedPost[-1]=="."
               user.word_number=user.word_number+len(generatedPost.split())
               user.save()
               return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]!=',' and generatedPost[-1]!='.':                
               generatedPost=generatedPost+"."
               user.word_number=user.word_number+len(generatedPost.split())
               user.save()
               return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]=='.':               
               user.word_number=user.word_number+len(generatedPost.split())
               user.save()
               return Response({"message": generatedPost}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             if url!="":
                prompt = promptPostUrlSpanish
             elif url=="":
                prompt = promptPostNonUrlSpanish             
             generatedPost = generatingContentByOpenai(prompt)
             if generatedPost[-1]==",":                
              generatedPost[-1]=="."
              user.word_number=user.word_number+len(generatedPost.split())
              user.save()
              return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]!=',' and generatedPost[-1]!='.':                
              generatedPost=generatedPost+"."
              user.word_number=user.word_number+len(generatedPost.split())
              user.save()
              return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]=='.':                 
               user.word_number=user.word_number+len(generatedPost.split())
               user.save()
               return Response({"message": generatedPost}, status=status.HTTP_200_OK)
        elif (user.usage_count==3 and user.word_number==0 )and (user.subscribed==False and user.word_number<user.word_limit):
            return Response({"message": "free"}, status=status.HTTP_201_CREATED)
        elif (user.usage_count==3 and user.word_number!=0 )and (user.subscribed==False and user.word_number<user.word_limit):
            subject = request.GET.get('subject')
            url= request.GET.get('url')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            socialType=request.GET.get('post')
            promptPostUrlEnglish = functionPromptPostUrlEnglish(subject, url, emotion, language, socialType)
            promptPostNonUrlEnglish = functionPromptPostNonUrlEnglish(subject, url, emotion, language, socialType)
            promptPostUrlSpanish = functionPromptPostUrlSpanish(subject, url, emotion, language, socialType)
            promptPostNonUrlSpanish = functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType)
            if language=="English":
             if url!="":
                prompt = promptPostUrlEnglish
             elif url=="":
                prompt = promptPostNonUrlEnglish             
             generatedPost = generatingContentByOpenai(prompt)
             if generatedPost[-1]==",":               
              generatedPost[-1]=="."
              user.word_number=user.word_number+len(generatedPost.split())
              user.save()
              return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]!=',' and generatedPost[-1]!='.':               
              generatedPost=generatedPost+"."
              user.word_number=user.word_number+len(generatedPost.split())
              user.save()
              return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]=='.':               
               user.word_number=user.word_number+len(generatedPost.split())
               user.save()
               return Response({"message": generatedPost}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             if url!="":
                prompt = promptPostUrlSpanish
             elif url=="":
                prompt = promptPostNonUrlSpanish             
             generatedPost = generatingContentByOpenai(prompt)       
             if generatedPost[-1]==",":            
              generatedPost[-1]=="."
              user.word_number=user.word_number+len(generatedPost.split())
              user.save()
              return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]!=',' and generatedPost[-1]!='.':          
              generatedPost=generatedPost+"."
              user.word_number=user.word_number+len(generatedPost.split())
              user.save()
              return Response({"message": generatedPost}, status=status.HTTP_200_OK)
             elif generatedPost[-1]=='.':            
               user.word_number=user.word_number+len(generatedPost.split())
               user.save()
               return Response({"message": generatedPost}, status=status.HTTP_200_OK)
            
        elif user.usage_count >3 and (user.subscribed==False and user.word_number<user.word_limit):
            subject = request.GET.get('subject')
            url = request.GET.get('url')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            socialType=request.GET.get('post')
            promptPostUrlEnglish = functionPromptPostUrlEnglish(subject, url, emotion, language, socialType)
            promptPostNonUrlEnglish = functionPromptPostNonUrlEnglish(subject, url, emotion, language, socialType)
            promptPostUrlSpanish = functionPromptPostUrlSpanish(subject, url, emotion, language, socialType)
            promptPostNonUrlSpanish = functionPromptPostNonUrlSpanish(subject, url, emotion, language, socialType)
            if language=="English":
             if url!="":
                prompt = promptPostUrlEnglish
             elif url=="":
                prompt = promptPostNonUrlEnglish             
             content = generatingContentByOpenai(prompt)
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_201_CREATED)
            elif language=="Spanish":
             if url!="":
                prompt = promptPostUrlSpanish
             elif url=="":
                prompt = promptPostNonUrlSpanish             
             content = generatingContentByOpenai(prompt)
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_200_OK)
        
        elif user.word_number>=user.word_limit:             
            user.subscribed=False
            user.word_number=0
            user.save()    
            return Response({"message": "limit"}, status=status.HTTP_201_CREATED)    




async def make_request(url, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            return await response.text()

@csrf_exempt    
def generateImageCasePost(request):
    if request.method == 'POST':
        email_info = json.loads(request.body)
        content = email_info.get('content')
        content=translator(content)                 
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
        headers ={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-QJ3pj9ignXLZT8IgAG8tkggeVkzFQj61gZKmIxOcFVaSMIsP"}
        data = {
                "steps": 40,
                "width": 512,
                "height": 512,
                "seed": 0,
                "cfg_scale": 5,
                "samples": 1,
                "style_preset": "enhance",
                "text_prompts": [
                {
                "text": content,
                "weight": 1
                },
                {
                "text": "non realistic thing",
                "weight": -1
                }
            ],

            }
     
        response = requests.post(url, json=data, headers=headers)
        sleep(5)
        data = response.json()
        for i, image in enumerate(data["artifacts"]):
                with open(f"D:/JCS-image/spain backend/emotion/v1_txt2img_{i}.png", "wb") as f:
                        f.write(base64.b64decode(image["base64"]))
        return JsonResponse({"url":"okay"})                


@csrf_exempt    
def generateImageCaseArticle(request):
    if request.method == 'POST':
        email_info = json.loads(request.body)
        content = email_info.get('content')
        content=summaryArticle(content)     
        string_data = client.images.generate(
                model="dall-e-3",
                prompt=content,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json"
                )
        
        string_data=str(string_data)
        start_index = string_data.find("b64_json=") + len("b64_json=")
        end_index = string_data.find(",", start_index)
        b64_json = string_data[start_index:end_index]
        with open(f"D:/JCS-image/spain backend/emotion/a.png", "wb") as f:  ## Generating Image usng OpenAI
                        f.write(base64.b64decode(b64_json))       
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
        headers ={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-QJ3pj9ignXLZT8IgAG8tkggeVkzFQj61gZKmIxOcFVaSMIsP"}
        data = {
                "steps": 40,
                "width": 512,
                "height": 512,
                "seed": 0,
                "cfg_scale": 5,
                "samples": 1,
                "style_preset": "enhance",
                "text_prompts": [
                {
                "text": content1,
                "weight": 1
                },
                {
                "text": "non realistic thing",
                "weight": -1
                }
            ],

            }
        response = requests.post(url, json=data, headers=headers)
        sleep(5)
        data = response.json()
        for i, image in enumerate(data["artifacts"]):
                    with open(f"D:/JCS-image/spain backend/emotion/v1_txt2img_{i}.png", "wb") as f:  ## Generating Image usng Stability
                        f.write(base64.b64decode(image["base64"]))
        return JsonResponse({"url":"okay"})                

        
def summary(content):
    content=content
    prompt=f'''Write a summary about {content}. Summary should be included 10 sentences.'''
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    content = res.choices[0].message.content
    return content

def summaryArticle(content):
    content=content
    prompt=f'''Write a summary about {content}. Summary should be included 10 sentences. Summary must be translated using English.'''
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    content = res.choices[0].message.content
    return content


def translator(content):
    content=content
    prompt=f'''Traslate {content} into English.'''
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    content = res.choices[0].message.content
    return content



class ArticleView(APIView):                   ## Article
    def get(self, request):
     user = request.user
     user=User.objects.get(pk=user.id)
     if user.email=="miriamlaof@gmail.com":
            title = request.GET.get('title')
            keyword = request.GET.get('keyword')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            if language=="English":
             prompt = funtionPromptArticleEnglish(title, keyword, emotion, language)         
             generatedArticle = generatingContentByOpenai(prompt)
             generatedArticle=contentChecking(generatedArticle)  
             return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             prompt = funtionPromptArticleSpanish(title, keyword, emotion, language)             
             generatedArticle = generatingContentByOpenai(prompt)
             generatedArticle= contentChecking(generatedArticle)
             return Response({"message": generatedArticle}, status=status.HTTP_200_OK)

     elif user.email!="miriamlaof@gmail.com":
        if user.usage_count < 3:
            user.usage_count += 1
            user.save()
            title= request.GET.get('title')
            keyword = request.GET.get('keyword')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            if language=="English":
             prompt = funtionPromptArticleEnglish(title, keyword, emotion, language)          
             generatedArticle = generatingContentByOpenai(prompt)
             generatedArticle=contentChecking(generatedArticle)               
             return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             prompt = funtionPromptArticleSpanish(title, keyword, emotion, language)             
             generatedArticle = generatingContentByOpenai(prompt)
             return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
        elif user.usage_count >=3 and (user.subscribed==False and user.word_limit==0 ):
             return Response({"message": "free"}, status=status.HTTP_201_CREATED)
        elif user.usage_count >=3 and (user.subscribed==True and user.word_number<user.word_limit):
            title= request.GET.get('title')
            keyword = request.GET.get('keyword')
            emotion =request.GET.get('checkedValues')
            language =request.GET.get('language')
            if language=="English":
             prompt = funtionPromptArticleEnglish(title, keyword, emotion, language)                     
             generatedArticle = generatingContentByOpenai(prompt)
             if generatedArticle[-1]==",":            
              generatedArticle[-1]=="."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]!=',' and generatedArticle[-1]!='.':          
              generatedArticle=generatedArticle+"."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]=='.':            
               user.word_number=user.word_number+len(generatedArticle.split())
               user.save()
               return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             prompt =funtionPromptArticleSpanish(title, keyword, emotion, language)             
             generatedArticle = generatingContentByOpenai(prompt)
             if generatedArticle[-1]==",":         
              generatedArticle[-1]=="."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]!=',' and generatedArticle[-1]!='.':            
              generatedArticle=generatedArticle+"."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]=='.':  
               user.word_number=user.word_number+len(generatedArticle.split())
               user.save()
               return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
        elif (user.usage_count==3 and user.word_number==0 )and (user.subscribed==False and user.word_number<user.word_limit):
            return Response({"message": "free"}, status=status.HTTP_201_CREATED)
        elif (user.usage_count==3 and user.word_number!=0 )and (user.subscribed==False and user.word_number<user.word_limit):
            title = request.GET.get('title')
            keyword= request.GET.get('keyword')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            if language=="English":
             prompt = funtionPromptArticleEnglish(title, keyword, emotion, language)
             generatedArticle = generatingContentByOpenai(prompt)
             if generatedArticle[-1]==",":              
              generatedArticle[-1]=="."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]!=',' and generatedArticle[-1]!='.':         
              generatedArticle=generatedArticle+"."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]=='.':             
               user.word_number=user.word_number+len(generatedArticle.split())
               user.save()
               return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
            elif language=="Spanish":
             prompt = funtionPromptArticleSpanish(title, keyword, emotion, language)             
             generatedArticle = generatingContentByOpenai(prompt)      
             if generatedArticle[-1]==",":          
              generatedArticle[-1]=="."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]!=',' and generatedArticle[-1]!='.':              
              generatedArticle=generatedArticle+"."
              user.word_number=user.word_number+len(generatedArticle.split())
              user.save()
              return Response({"message": generatedArticle}, status=status.HTTP_200_OK)
             elif generatedArticle[-1]=='.':           
               user.word_number=user.word_number+len(generatedArticle.split())
               user.save()
               return Response({"message": generatedArticle}, status=status.HTTP_200_OK)          
        elif user.usage_count >3 and (user.subscribed==False and user.word_number<user.word_limit):
            title = request.GET.get('title')
            keyword = request.GET.get('keyword')
            emotion=request.GET.get('checkedValues')
            language=request.GET.get('language')
            if language=="English":
             prompt = funtionPromptArticleEnglish(title, keyword, emotion, language)             
             content=generatingContentByOpenai(prompt)
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_201_CREATED)
            elif language=="Spanish":
             prompt = prompt = funtionPromptArticleSpanish(title, keyword, emotion, language)
             content = generatingContentByOpenai(prompt)
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_200_OK)       
        elif user.word_number>=user.word_limit:            
            user.subscribed=False
            user.word_number=0
            user.save()    
            return Response({"message": "limit"}, status=status.HTTP_201_CREATED)
            
class ProductA(APIView):
    def get(self, request):
        user = request.user
        domain_url = 'https://emotionseo.ai/generatearticle'
        cancelurl='https://emotionseo.ai/precios'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url,
                cancel_url=cancelurl,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_IDA,
                        'quantity': 1,
                    }
                ]
            )
            user = User.objects.get(id=user.id)           
            user.word_limit = 20000
            user.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})       
        return Response({"message": "Subscription successful. You can continue using the service"}, status=status.HTTP_200_OK)


class ProductB(APIView):    
    def get(self, request):
        user = request.user
        domain_url = 'https://emotionseo.ai/generatearticle'
        cancelurl='https://emotionseo.ai/precios'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url,
                cancel_url=cancelurl,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_IDB,
                        'quantity': 1,
                    }
                ]
            )
            user = User.objects.get(id=user.id)
            user.word_limit = 50000
            user.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        
        return Response({"message": "Subscription successful. You can continue using the service"}, status=status.HTTP_200_OK)

class ProductC(APIView):    
    def get(self, request):
        user=request.user
        domain_url = 'https://emotionseo.ai/generatearticle'
        cancelurl='https://emotionseo.ai/precios'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url,
                cancel_url=cancelurl,
                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_IDC,
                        'quantity': 1,
                    }
                ]
            )
            user = User.objects.get(id=user.id)
            user.word_limit = 100000
            user.save()
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})        
        return Response({"message": "Subscription successful. You can continue using the service"}, status=status.HTTP_200_OK)

class GetInfo(APIView):
    def get(self, request):
        user=request.user
        user = User.objects.get(id=user.id)
        word_limit=user.word_limit
        generated_word=user.word_number
        rest_word=word_limit-generated_word
        first_name = user.first_name
        last_name=user.last_name
        subscribed=user.subscribed        
        return Response({ "last":last_name,"word_limit":word_limit,"generated_word":generated_word, "rest_word":rest_word, "first":first_name,"subscribed":subscribed}, status=status.HTTP_200_OK)

class Invoice(APIView):
    def get(self, request):
        user = request.user
        user=User.objects.get(id=user.id)       
        city = request.GET.get('city')
        postalcode = request.GET.get('postalcode')       
        home = request.GET.get('home')
        dni = request.GET.get('dni')
        company_name=request.GET.get('cname')
        user.city=city
        user.postalcode=postalcode
        user.home=home
        user.dni=dni
        user.companyname=company_name
        user.save()
        template = get_template('pdf.html')
        context = {'first_name': user.first_name, 'last_name':user.last_name, 'companyname':user.companyname, 'city':user.city, 'postalcode':user.postalcode,
        'home':user.home, 'dni':user.dni, 'currenttime':user.current_time, 'email':user.email}
        html = template.render(context)
        pdf_file_path = 'invoice.pdf'
        with open(pdf_file_path, 'w+b') as pdf_file:
            pisa_status = pisa.CreatePDF(html, dest=pdf_file)
        with open(pdf_file_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        email = EmailMessage(
            'Invoice',
            'Please find attached the invoice',
            'hola@emotionseo.ai',
            ['handsome176743@gmail.com'],
        )
        email.attach('invoice.pdf', pdf_data, 'application/pdf')
        email.send()
        os.remove(pdf_file_path)
        pdf_file.close()
        return Response({"message": "Subscription successful. You can continue using the service"}, status=status.HTTP_200_OK)

class ValidateOTP(APIView):
    permission_classes=[AllowAny]
    def get(self, request):
        otp = request.GET.get('otp')      
        try:
            user=User.objects.get(otp=otp)          
        except User.DoesNotExist:
            return Response({'error':'User with this email does not exist'}, status=status.HTTP_201_CREATED)
        if user.otp==otp:
            user.otp=None
            user.save()
            return Response({'token':'okay'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid OTP'}, status=status.HTTP_201_CREATED)
        
class DeleteAccount(APIView):
    def post(self, request):           
        username=request.data.get('usernameinfo')
        user=User.objects.get(username=username)
        user.delete()        
        return Response({'message':'okay'}, status=status.HTTP_200_OK)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"success"},status=status.HTTP_204_NO_CONTENT)

def generatingSEOKeywords(request):               ## Generating 10 SEO keywords
    data=request.GET.get("title")
    language=request.GET.get("language")   
    if language=='English':   
     client = OpenAI(api_key = api_key)
     prompt = f"write 10 SEO keywords related to \"{data}\" without integer and breaking line. Ten keywords should be separated by commas."
     content = generatingContentByOpenai(prompt)
     return JsonResponse({'keyword':content})
    elif language=="Spanish":    
     prompt = f"escriba 10 palabras clave SEO relacionadas con \"{data}\" sin números enteros ni líneas de separación. Diez palabras clave deben estar separadas por comas."    
     content = generatingContentByOpenai(prompt)  
     return JsonResponse({'keyword':content})

User = get_user_model()
@csrf_exempt
def resetPassword(request):
    if request.method == 'POST':
        email_info = json.loads(request.body)
        email = email_info.get('email')      
        user = User.objects.get(email=email)
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_password_link ='https://emotionseo.ai:8000/user/reset_password/confirm/'+uid+'/'+token+'/'
            send_mail(
                'Reset Your Password',
                f'Click the following link to reset your password: {reset_password_link}',
                'hola@emotionseo.ai',
                [email]
            )
        return JsonResponse({'message': 'Password reset link has been sent to your email'})
    return JsonResponse({'error': 'Invalid request'})

@csrf_exempt
def forgotNew(request):
    if request.method == 'POST':
        email_info = json.loads(request.body)
        email = email_info.get('email')     
        user = User.objects.get(email=email)
        if user:          
         return JsonResponse({'message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"message":"error"}, status=status.HTTP_201_OK)
    return JsonResponse({'error': 'Invalid request'})

User = get_user_model()
uid=0
def reset_password_confirm(request, uidb64, token):
    try:
        global uid 
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):        
        return HttpResponseRedirect("https://emotionseo.ai/resetpage")
    else:
        messages.error(request, 'The reset password link is invalid.')
        return HttpResponseRedirect('https://emotionseo.ai/login') 

@csrf_exempt    
def confirm_password(request):
    if request.method == 'POST':
        user = User.objects.get(pk=uid)
        password_info = json.loads(request.body)
        new_password = password_info.get('newpassword')
        confirm_password = password_info.get('confirmpassword')
        if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your password has been reset. You can now log in with your new password.')
                return JsonResponse({"message":"okay"}, status=status.HTTP_200_OK) # Redirect to the login page
        else:
            messages.error(request, 'Passwords do not match.')
            JsonResponse({"message":"again"}, status=status.HTTP_201_CREATED)
        
stripe.api_key = settings.STRIPE_SECRET_KEY
@csrf_exempt
def stripe_webhook(request):        
    payload = request.body  
    payload=json.loads(payload)        
    # Handle the checkout.session.completed event
    if payload['type'] == 'checkout.session.completed':
        # Fetch all the required data from session
        client_reference_id = payload['data']['object']['client_reference_id']
        stripe_subscription_id = payload['data']['object']['subscription']
        # Get the user and create a new StripeCustomer
        try:
         user = User.objects.get(id=client_reference_id)
         user.subscriptionid=stripe_subscription_id      
         user.subscribed = True
         user.save()
        except:
         print("Error: Invalid conversion to integer")
    return HttpResponse(status=200)
   
class CancelSubscription(APIView):
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        user=request.user 
        user_instance = User.objects.get(id=user.id)        
        subscription_id=user_instance.subscriptionid
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True)
        user.subscribed=False        
        user.save()
        return JsonResponse({"message":"okay"}, status=status.HTTP_200_OK)
    
class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data
        code = validated_data.get('code')
        error = validated_data.get('error')
        # code = request.query_params.get('code')
        # error = request.query_params.get('error')

        login_url = f'{settings.BASE_FRONTEND_URL}'
        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = 'https://emotionseo.ai/google'
        access_token = google_get_access_token(code=code,
                                               redirect_uri=redirect_uri)
        user_data = google_get_user_info(access_token=access_token)

        try:
            user = User.objects.get(email=user_data['email'])
            access_token, refresh_token = generate_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
         
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            username = user_data['email'].split('@')[0]
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')
            user = User.objects.create(
                username=username,
                email=user_data['email'],
                first_name=first_name,
                last_name=last_name,
               
            )

            access_token, refresh_token = generate_tokens_for_user(user)
            response_data = {
                'user': UserSerializer(user).data,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
            return Response(response_data, status=status.HTTP_200_OK)
           
def display_stability_image(request):
    # Path to the image file
    image_path = "./v1_txt2img_0.png"
    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        image_data = f.read()
    # Set the appropriate content type
    response = HttpResponse(image_data, content_type='image/png')
    return HttpResponse(image_data, content_type='image/png')

def display_openai_image(request):
    image_path = "./a.png"
    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        image_data = f.read()
    # Set the appropriate content type
    response = HttpResponse(image_data, content_type='image/png')
    return HttpResponse(image_data, content_type='image/png')



