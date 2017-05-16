import boto3 
from boto3 import dynamodb 
from boto3.session import Session
import uuid
import json
import time
import datetime
dynamodb=boto3.resource('dynamodb',region_name='us-west-2',aws_access_key_id='',aws_secret_access_key='')

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):

    method=event['httpMethod']
    if method=='POST':
          table=dynamodb.Table('orders')
    	  response = table.put_item(
          	Item={
         	   'menu_id':event['menu_id'],
            	   'order_id':event['order_id'],
            	   'customer_name':event['customer_name'],
            	   'customer_email':event['customer_email'],
            	   'order_status': 'processing',
            	   "order": {  }
          	 })
    	  table=dynamodb.Table('pizza')     
    	  response=table.get_item(
        	Key={
            	  'menu_id':event['menu_id']
        	})
          if(response['Item']['sequence'][0]=='selection'):    
               result=""
               result+="Hi "+event['customer_name']
               result+=", please choose one of these selection:"
               value=1
               for i in response['Item']['selection']:
                   result+=(" "+str(value)+". "+str(i)+",")
                   value+=1
               result=result[:-1]
          else: 
               result=""
               result+="Hi "+event['customer_name']
               result+="Which size do you want?"
               value=1
               for i in response['Item']['size']:
                  result+=(" "+str(value)+". "+str(i)+",")
                  value+=1
               result=result[:-1]    
          return {"Message": result}
    elif (method=='PUT'):
          table=dynamodb.Table('orders')
          response = table.get_item(
       		 Key={
              		'order_id':event['order_id'],
          		})
          order_map = response['Item']['order']
    	  table=dynamodb.Table('pizza')
          menu_details=table.get_item(
       		Key={
                   'menu_id':response['Item']['menu_id'] 
         	})
          if (menu_details['Item']['sequence'][0]=='selection'):
               if 'selection' not in order_map:
            	result=""
                input_number=int(event['input'])
                result+="Which size do you want?"
                value=1
                for i in menu_details['Item']['size']:
                  result+=(" "+str(value)+". "+str(i)+",")
                  value+=1
                result=result[:-1] 
                if((input_number-1)<(len(menu_details['Item']['selection']))):
                    order_selection={"selection":menu_details['Item']['selection'][input_number-1]}
                else:
                    return "Please select from available options."
                table=dynamodb.Table('orders')
                res=table.update_item(
                   Key={
                        'order_id':event['order_id']
                       },
                       UpdateExpression= "SET #n= :value1",
                       ExpressionAttributeNames = {"#n":"order"},
                       ExpressionAttributeValues={':value1': order_selection})
                return {"Message":result}
               elif 'size' not in order_map:
            	input_number=int(event['input']) 
                if((input_number-1)<(len(menu_details['Item']['size']))):
            	   order_size=menu_details['Item']['size'][input_number-1]
                else:
                   return "Please select from available options."
            	update_map={}
            	update_map['selection']=response['Item']['order']['selection']
            	update_map['size']=order_size
            	order_price=menu_details['Item']['price'][input_number-1]
            	update_map['costs']=order_price
            	update_map['order_time']=str(datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S'))
            	table=dynamodb.Table('orders')
                res=table.update_item(
                Key={
                    'order_id':event['order_id']
                    },
                UpdateExpression= "SET order_status= :value1,#n= :value2",
                ExpressionAttributeNames = {"#n":"order"},
                ExpressionAttributeValues={":value1": "processing",':value2':update_map})
                result=""
                result+="Your order costs $"+order_price+". We will email you when the order is ready. Thank you!"
                return {"Message":result} 
               else:
            	return "Please select from the available options."
          elif (menu_details['Item']['sequence'][0]=='size'):
               if 'size' not in order_map:
            	   result="" 
                   result+='please choose one of these selection:'
                   value=1
            	   for i in menu_details['Item']['selection']:
                      result+=(" "+str(value)+". "+str(i)+",")
                      value+=1
                   result=result[:-1]
            	   input_number=int(event['input']) 
                   if((input_number-1)<(len(menu_details['Item']['size']))):
                         order_size=menu_details['Item']['size'][input_number-1]
                   else:
                         return "Please select from the available options."
                   update_map={}
                   #update_map['selection']=response['Item']['order']['selection']
                   update_map['size']=order_size
                   order_price=menu_details['Item']['price'][input_number-1]
                   update_map['costs']=order_price
                   update_map['order_time']=datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S')
                   table=dynamodb.Table('orders')
                   res=table.update_item(
                	Key={
                    		'order_id':event['order_id']
                    	},
                	UpdateExpression= "SET order_status= :value1,#n= :value2",
                	ExpressionAttributeNames = {"#n":"order"},
                	ExpressionAttributeValues={":value1": "processing",':value2':update_map})
                   return {"Message":result}  
               elif 'selection' not in order_map:
                   input_number=int(event['input'])
                   if((input_number-1)<(len(menu_details['Item']['selection']))):
            	       order_selection={"selection":menu_details['Item']['selection'][input_number-1]}
                   else:
                       return "Please select from the available options."
            	   order_selection['size']=response['Item']['order']['size']
            	   order_selection['costs']=response['Item']['order']['costs']
            	   order_selection['order_time']=response['Item']['order']['order_time']
            	   table=dynamodb.Table('orders')
                   res=table.update_item(
                	Key={
                          'order_id':event['order_id']
                        },
                        UpdateExpression= "SET #n= :value1",
                	ExpressionAttributeNames = {"#n":"order"},
                	ExpressionAttributeValues={':value1': order_selection})
                   result=""
            	   result+="Your order costs $"+order_selection['costs']+'. We will email you when the order is ready. Thank you!'
                   return {"Message":result} 
               else: 
            	   return "Please select from the available options."   
    elif (method=='GET'):
         table=dynamodb.Table('orders')
         try:
             response=table.get_item(
      	  		Key={
                        'order_id':event['order_id']
             })
             return response['Item'] 
         except KeyError:return "400"
         
    else:
        return respond(ValueError('Unsupported method'))
