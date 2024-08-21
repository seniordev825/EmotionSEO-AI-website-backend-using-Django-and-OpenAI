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
client = OpenAI(
    api_key = api_key
)



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

class PostView(APIView):
    def get(self, request):
     user = request.user
     user=User.objects.get(pk=user.id)
     
     if user.email=="miriamlaof@gmail.com":
            key1 = request.GET.get('subject')
            key2 = request.GET.get('url')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            key5=request.GET.get('post')
            if key4=="English":
             if key2!="":
              prompt = f'''Write a post for {key5} in English. The post must include the site information with {key2}. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
             elif key2=="":
                prompt = f'''Write a post for {key5} in English. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
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

             
             if content[-1]==",":
              a=content  
              a[-1]=="."
              
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             if key2!="":

                  prompt = f'''Escribe un post para {key5} en Español. El post debe incluir la información del sitio con {key2}. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
             elif key2=="":
                prompt = f'''Escribe un post para {key5} en Español. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''

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
             

             
              

            
             if content[-1]==",":
              a=content  
              a[-1]=="."
              
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               
               return Response({"message": c}, status=status.HTTP_200_OK)

     elif user.email!="miriamlaof@gmail.com":
        if user.usage_count < 3:
       
            user.usage_count += 1
            user.save()
            key1 = request.GET.get('subject')
            key2 = request.GET.get('url')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            key5=request.GET.get('post')
            if key4=="English":
             if key2!="":
              prompt = f'''Write a post for {key5} in English. The post must include the site information with {key2}. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
             elif key2=="":
                prompt = f'''Write a post for {key5} in English. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             if key2!="":

                  prompt = f'''Escribe un post para {key5} en Español. El post debe incluir la información del sitio con {key2}. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa.. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
             elif key2=="":
                prompt = f'''Escribe un post para {key5} en Español. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
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
             return Response({"message": content}, status=status.HTTP_200_OK)
        elif user.usage_count >=3 and (user.subscribed==False and user.word_limit==0 ):
             return Response({"message": "free"}, status=status.HTTP_201_CREATED)

        elif user.usage_count >=3 and (user.subscribed==True and user.word_number<user.word_limit):
            key1 = request.GET.get('subject')
            key2 = request.GET.get('url')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            key5=request.GET.get('post')

            if key4=="English":

             if key2!="":
              prompt = f'''Write a post for {key5} in English. The post must include the site information with {key2}. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
             elif key2=="":
                prompt = f'''Write a post for {key5} in English. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
             res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             if key2!="":

                  prompt = f'''Escribe un post para {key5} en Español. El post debe incluir la información del sitio con {key2}. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
             elif key2=="":
                prompt = f'''Escribe un post para {key5} en Español. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
        elif (user.usage_count==3 and user.word_number==0 )and (user.subscribed==False and user.word_number<user.word_limit):
            return Response({"message": "free"}, status=status.HTTP_201_CREATED)

        elif (user.usage_count==3 and user.word_number!=0 )and (user.subscribed==False and user.word_number<user.word_limit):
            key1 = request.GET.get('subject')
            key2 = request.GET.get('url')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            key5=request.GET.get('post')
            if key4=="English":

             if key2!="":
              prompt = f'''Write a post for {key5} in English. The post must include the site information with {key2}. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
             elif key2=="":
                prompt = f'''Write a post for {key5} in English. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             if key2!="":

                  prompt = f'''Escribe un post para {key5} en Español. El post debe incluir la información del sitio con {key2}. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
             elif key2=="":
                prompt = f'''Escribe un post para {key5} en Español. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
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
             print(content[-1])
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
                

               
            
        elif user.usage_count >3 and (user.subscribed==False and user.word_number<user.word_limit):
            key1 = request.GET.get('subject')
            key2 = request.GET.get('url')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            key5=request.GET.get('post')
            if key4=="English":

             if key2!="":
              prompt = f'''Write a post for {key5} in English. The post must include the site information with {key2}. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
             elif key2=="":
                prompt = f'''Write a post for {key5} in English. Post should not be too long.
Write the post to engage your target audience, give advice, provide immediate value, and motivate a specific action, which is essential for effective {key5} marketing.
The post must include emoticons. The content must be optimized for SEO. The post must be written with {key3}.
The topic of this post should be {key1} and do not change or add anything.
The last sentence of the post must be a meaningful and complete sentence. The last sentence must be ended a full stop. Add the appropriate hashtags.
We want this content to be highly searchable.'''
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
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_201_CREATED)
            elif key4=="Spanish":
             if key2!="":

                  prompt = f'''Escribe un post para {key5} en Español. El post debe incluir la información del sitio con {key2}. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
             elif key2=="":
                prompt = f'''Escribe un post para {key5} en Español. El post no debe ser muy largo
Escribe el post para atraer al público objetivo, dar consejos, proporcionar valor inmediato y motivar una acción específica, lo cual es esencial para un marketing de {key5} efectivo.
El post debe incluir emoticonos. El contenido debe estar optimizado para SEO. El post debe estar escrito con {key3}.
El tema de esta publicación debe ser {key1} y no cambie ni agregue nada.
La última frase del post debe ser una frase significativa y completa. La última frase debe terminar con un punto. Añade los hashtags adecuados.
Queremos que este contenido sea altamente buscable.'''
            
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
def generateimage1(request):
    if request.method == 'POST':
        email_info = json.loads(request.body)
        content = email_info.get('content')
        content1=translator(content)
       
        
        string_data = client.images.generate(
                model="dall-e-3",
                prompt=content,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json"
                )
        # print(response)
        
        string_data=str(string_data)
        start_index = string_data.find("b64_json=") + len("b64_json=")
        end_index = string_data.find(",", start_index)
        b64_json = string_data[start_index:end_index]


        with open(f"D:/JCS-image/spain backend/emotion/a.png", "wb") as f:
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
                with open(f"D:/JCS-image/spain backend/emotion/v1_txt2img_{i}.png", "wb") as f:
                        f.write(base64.b64decode(image["base64"]))
        return JsonResponse({"url":"okay"})                


@csrf_exempt    
def generateimage(request):
    if request.method == 'POST':
        email_info = json.loads(request.body)
        content = email_info.get('content')
        content1=summaryarticle(content)
        
        
        string_data = client.images.generate(
                model="dall-e-3",
                prompt=content1,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json"
                )
        # print(response)
        
        string_data=str(string_data)
        start_index = string_data.find("b64_json=") + len("b64_json=")
        end_index = string_data.find(",", start_index)
        b64_json = string_data[start_index:end_index]


        with open(f"D:/JCS-image/spain backend/emotion/a.png", "wb") as f:
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
                    with open(f"D:/JCS-image/spain backend/emotion/v1_txt2img_{i}.png", "wb") as f:
                        f.write(base64.b64decode(image["base64"]))
        return JsonResponse({"url":"okay"})                

        
def summary(content):
    a=content
    prompt=f'''Write a summary about {a}. Summary should be included 10 sentences.'''
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    content1 = res.choices[0].message.content
    return content1

def summaryarticle(content):
    a=content
    prompt=f'''Write a summary about {a}. Summary should be included 10 sentences. Summary must be translated using English.'''
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    content1 = res.choices[0].message.content
    return content1


def translator(content):
    a=content
    prompt=f'''Traslate {a} into English.'''
    res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    content1 = res.choices[0].message.content
    return content1
    
class FreeServiceUsageView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
     user = request.user
     user=User.objects.get(pk=user.id)
     
     if user.email=="miriamlaof@gmail.com":
            key1 = request.GET.get('title')
            key2 = request.GET.get('keyword')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            if key4=="English":
             prompt = f'''Write article in English. The article must be SEO-Optmized Content and the article must be included {key2}
        The article must be written with {key3}.The article should typically contain 750 words. The last sentence of article must be a meaningfull and complete sentence. The last sentence must be ended a full stop.
        The title of article must be {key1} and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the article naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the article easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''
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
            
             
               
            
             if content[-1]==",":
              a=content  
              a[-1]=="."
              
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             prompt = f'''Escribe un artículo en español.  El artículo debe ser contenido optimizado para SEO y debe incluir {key2}. 
         El artículo debe estar escrito con {key3}. Normalmente, el artículo debe contener 750 palabras. La última frase del artículo debe ser una frase significativa y completa. La ultima frase debe estar completa y terminar siempre el articulo con un ".".
        El título del artículo debe ser {key1} y no cambies ni agregues nada, ¡y escribe con una fuente más grande que el contenido!
        Queremos que este contenido sea altamente buscable.
        Escribe el artículo de manera natural y evita comentarios o palabras (por ejemplo: contenido optimizado para SEO) que no estén relacionados con el tema.
        No incluyas símbolos innecesarios como ---, ###, **, etc.
        Añade saltos de línea, guiones e indentaciones para hacer que el artículo sea fácil de leer y entender.
        Debes considerar distinguir con precisión entre título, contenido, párrafos, etc.
        Escribe las nuevas oraciones en nuevas filas.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               
               return Response({"message": c}, status=status.HTTP_200_OK)

     elif user.email!="miriamlaof@gmail.com":
        if user.usage_count < 3:
            # Allow access to the service
            user.usage_count += 1
            user.save()
            key1 = request.GET.get('title')
            key2 = request.GET.get('keyword')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            if key4=="English":
             prompt = f'''Write article in English. The article must be SEO-Optmized Content and the article must be included {key2}
        The article must be written with {key3}.The article should typically contain 750 words. The last sentence of article must be a meaningfull and complete sentence. The last sentence must be ended a full stop.
        The title of article must be {key1} and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the article naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the article easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             prompt = f'''Escribe un artículo en español.  El artículo debe ser contenido optimizado para SEO y debe incluir {key2}. 
         El artículo debe estar escrito con {key3}. Normalmente, el artículo debe contener 750 palabras. La última frase del artículo debe ser una frase significativa y completa. La ultima frase debe estar completa y terminar siempre el articulo con un ".".
        El título del artículo debe ser {key1} y no cambies ni agregues nada, ¡y escribe con una fuente más grande que el contenido!
        Queremos que este contenido sea altamente buscable.
        Escribe el artículo de manera natural y evita comentarios o palabras (por ejemplo: contenido optimizado para SEO) que no estén relacionados con el tema.
        No incluyas símbolos innecesarios como ---, ###, **, etc.
        Añade saltos de línea, guiones e indentaciones para hacer que el artículo sea fácil de leer y entender.
        Debes considerar distinguir con precisión entre título, contenido, párrafos, etc.
        Escribe las nuevas oraciones en nuevas filas.'''
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
             return Response({"message": content}, status=status.HTTP_200_OK)
        elif user.usage_count >=3 and (user.subscribed==False and user.word_limit==0 ):
             return Response({"message": "free"}, status=status.HTTP_201_CREATED)

        elif user.usage_count >=3 and (user.subscribed==True and user.word_number<user.word_limit):
            key1 = request.GET.get('title')
            key2 = request.GET.get('keyword')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')

            if key4=="English":

             prompt = f'''Write article in English. The article must be SEO-Optmized Content and the article must be included {key2}.
        The article must be written with {key3}. The article should typically contain 750 words. The last sentence of article must be a meaningfull and complete sentence. The last sentence must be ended a full stop.
        The title of article must be {key1} and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the article naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the article easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''
             res=client.chat.completions.create(
         model = "gpt-4-1106-preview",
         max_tokens = 1048,
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             prompt = f'''Escribe un artículo en español.  El artículo debe ser contenido optimizado para SEO y debe incluir {key2}. 
         El artículo debe estar escrito con {key3}. Normalmente, el artículo debe contener 750 palabras. La última frase del artículo debe ser una frase significativa y completa. La ultima frase debe estar completa y terminar siempre el articulo con un ".".
        El título del artículo debe ser {key1} y no cambies ni agregues nada, ¡y escribe con una fuente más grande que el contenido!
        Queremos que este contenido sea altamente buscable.
        Escribe el artículo de manera natural y evita comentarios o palabras (por ejemplo: contenido optimizado para SEO) que no estén relacionados con el tema.
        No incluyas símbolos innecesarios como ---, ###, **, etc.
        Añade saltos de línea, guiones e indentaciones para hacer que el artículo sea fácil de leer y entender.
        Debes considerar distinguir con precisión entre título, contenido, párrafos, etc.
        Escribe las nuevas oraciones en nuevas filas.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
        elif (user.usage_count==3 and user.word_number==0 )and (user.subscribed==False and user.word_number<user.word_limit):
            return Response({"message": "free"}, status=status.HTTP_201_CREATED)

        elif (user.usage_count==3 and user.word_number!=0 )and (user.subscribed==False and user.word_number<user.word_limit):
            key1 = request.GET.get('title')
            key2 = request.GET.get('keyword')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            if key4=="English":

             prompt = f'''Write article in English. The article must be SEO-Optmized Content and the article must be included {key2}.
        The article must be written with {key3}. The article should typically contain 750 words. The last sentence of article must be a meaningfull and complete sentence. The last sentence must be ended a full stop.
        The title of article must be {key1} and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the article naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the article easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''
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
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
            elif key4=="Spanish":
             prompt = f'''Escribe un artículo en español.  El artículo debe ser contenido optimizado para SEO y debe incluir {key2}. 
         El artículo debe estar escrito con {key3}. Normalmente, el artículo debe contener 750 palabras. La última frase del artículo debe ser una frase significativa y completa. La última frase debe terminar con un punto.
        El título del artículo debe ser {key1} y no cambies ni agregues nada, ¡y escribe con una fuente más grande que el contenido!
        Queremos que este contenido sea altamente buscable.
        Escribe el artículo de manera natural y evita comentarios o palabras (por ejemplo: contenido optimizado para SEO) que no estén relacionados con el tema.
        No incluyas símbolos innecesarios como ---, ###, **, etc.
        Añade saltos de línea, guiones e indentaciones para hacer que el artículo sea fácil de leer y entender.
        Debes considerar distinguir con precisión entre título, contenido, párrafos, etc.
        Escribe las nuevas oraciones en nuevas filas.'''
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
       
             if content[-1]==",":
              a=content  
              a[-1]=="."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": a}, status=status.HTTP_200_OK)
             elif content[-1]!=',' and content[-1]!='.':
              b=content  
              b=b+"."
              user.word_number=user.word_number+len(content.split())
              user.save()
              return Response({"message": b}, status=status.HTTP_200_OK)
             elif content[-1]=='.':
               c=content  
               user.word_number=user.word_number+len(content.split())
               user.save()
               return Response({"message": c}, status=status.HTTP_200_OK)
                

               
            
        elif user.usage_count >3 and (user.subscribed==False and user.word_number<user.word_limit):
            key1 = request.GET.get('title')
            key2 = request.GET.get('keyword')
            key3=request.GET.get('checkedValues')
            key4=request.GET.get('language')
            if key4=="English":

             prompt = f'''Write article in English. The article must be SEO-Optmized Content and the article must be included {key2}.
        The article must be written with {key3}. The article should typically contain 750 words. The last sentence of article must be a meaningfull and complete sentence. The last sentence must be ended a full stop.
        The title of article must be {key1} and don't change or add anything and write with bigger font than content!
        We want this content to be high searchable.
        Write the article naturally and avoid comments or words(for example: SEO-Optimized Content) that are not related to the topic.
        Don't involve unnecessary symbols such as ---, ###, **, and so on.
        Add line breaks, dashes and indentations to make the article easy to read and understand.
        Must consider to accurately distinguish between title, content, paragraphes and so on.
        Write the new sentences on the new rows.'''
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
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_201_CREATED)
            elif key4=="Spanish":
             prompt = f'''Escribe un artículo en español.  El artículo debe ser contenido optimizado para SEO y debe incluir {key2}. 
         El artículo debe estar escrito con {key3}. Normalmente, el artículo debe contener 750 palabras. La última frase del artículo debe ser una frase significativa y completa. La última frase debe terminar con un punto.
        El título del artículo debe ser {key1} y no cambies ni agregues nada, ¡y escribe con una fuente más grande que el contenido!
        Queremos que este contenido sea altamente buscable.
        Escribe el artículo de manera natural y evita comentarios o palabras (por ejemplo: contenido optimizado para SEO) que no estén relacionados con el tema.
        No incluyas símbolos innecesarios como ---, ###, **, etc.
        Añade saltos de línea, guiones e indentaciones para hacer que el artículo sea fácil de leer y entender.
        Debes considerar distinguir con precisión entre título, contenido, párrafos, etc.
        Escribe las nuevas oraciones en nuevas filas.'''
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
             user.word_number=user.word_number+len(content.split())
             user.save()
             return Response({"message": content}, status=status.HTTP_200_OK)
        
        elif user.word_number>=user.word_limit:            
            user.subscribed=False
            user.word_number=0
            user.save()
    
            return Response({"message": "limit"}, status=status.HTTP_201_CREATED)
            


class Producta(APIView):
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


class Productb(APIView):
    
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

class GetInfo(APIView):
    #permission_classes = [IsAuthenticated]
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

class Productc(APIView):
    
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


class FreeServiceUsageView2(APIView):
    #permission_classes = [IsAuthenticated]
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

        # Read the PDF file
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
        

      

        # Create or update the invoice

        

        # Create or update the subscription
        

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
            return Response({'token':'okya'}, status=status.HTTP_200_OK)
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
        return Response({"a":"success"},status=status.HTTP_204_NO_CONTENT)




def generating(request):
    data=request.GET.get("title")
    language=request.GET.get("language")
    
    if language=='English':
    
     client = OpenAI(
    api_key = api_key)
     prompt = f"write 10 SEO keywords related to \"{data}\" without integer and breaking line. Ten keywords should be separated by commas."
     res=client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    
     content = res.choices[0].message.content

     return JsonResponse({'keyword':content})
    elif language=="Spanish":
     client = OpenAI(
    api_key =api_key)
     prompt = f"escriba 10 palabras clave SEO relacionadas con \"{data}\" sin números enteros ni líneas de separación. Diez palabras clave deben estar separadas por comas."
     res=client.chat.completions.create(
        model = "gpt-4-1106-preview",
        messages = [
            {"role": "system", "content": 'You write text based on my prompt.'
            },
            {"role": "user", "content": prompt},
        ]
    )
    
     content = res.choices[0].message.content
   
     return JsonResponse({'keyword':content})


User = get_user_model()
@csrf_exempt
def forgot(request):
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
def forgotnew(request):
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
        # user.cancel=True
        #user.word_number=0

        
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
           

def image(request):
    # Path to the image file
    image_path = "./v1_txt2img_0.png"

    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Set the appropriate content type
    response = HttpResponse(image_data, content_type='image/png')

    return HttpResponse(image_data, content_type='image/png')

def image1(request):

    image_path = "./a.png"

    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Set the appropriate content type
    response = HttpResponse(image_data, content_type='image/png')

    return HttpResponse(image_data, content_type='image/png')



