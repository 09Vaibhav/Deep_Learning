# -*- coding: utf-8 -*-
"""Copy of assignment_1_10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NxF6rneA6Hw4UeYOqO4TEQmg7BAN9seY
"""

import tensorflow as tf
from keras.datasets import fashion_mnist
from matplotlib import pyplot as plt


(train_X,train_Y),(test_X,test_Y) = tf.keras.datasets.mnist.load_data(path="mnist.npz")
train_X = train_X/255
test_X = test_X/255

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

class Neural_network:
    np.random.seed(10)
    def __init__(self,train_X,train_Y,inp_dim,hidden_layers_size,hidden_layers,output_dim,batch_size=30,epochs=10,activation_func="relu"
           ,learning_rate=6e-3 ,decay_rate=0.9,beta=0.9,beta1=0.9,beta2=0.99,optimizer="adam",weight_init="xavier",loss="cross_entropy"):

        self.train_X,self.x_cv,self.train_Y,self.y_cv = train_test_split(train_X, train_Y, test_size=0.10, random_state=100,stratify=train_Y)

        np.random.seed(10)
        self.inp_dim = inp_dim
        self.hidden_layers = hidden_layers
        self.hidden_layers_size = hidden_layers_size
        self.output_dim = output_dim

        self.batch = batch_size
        self.epochs = epochs
        self.activation_func = activation_func
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        self.optimizer = optimizer
        self.weight_init = weight_init
        self.beta = beta
        self.beta1 = beta1
        self.beta2 = beta2
        self.loss = loss

        self.layers = [self.inp_dim] + self.hidden_layers*[self.hidden_layers_size] + [self.output_dim]

        layers = self.layers.copy()
        self.weights = []
        self.biases = []
        self.activations = []
        self.activation_gradients = []
        self.weights_gradients = []
        self.biases_gradients = []

        for i in range(len(layers)-1):
            if self.weight_init == 'xavier':
                std = np.sqrt(2/(layers[i]*layers[i+1]))
                self.weights.append(np.random.normal(0,std,(layers[i],layers[i+1])))
                self.biases.append(np.random.normal(0,std,(layers[i+1])))
            else:
                self.weights.append(np.random.normal(0,0.5,(layers[i],layers[i+1])))
                self.biases.append(np.random.normal(0,0.5,(layers[i+1])))
            self.activations.append(np.zeros(layers[i]))
            self.activation_gradients.append(np.zeros(layers[i+1]))
            self.weights_gradients.append(np.zeros((layers[i],layers[i+1])))
            self.biases_gradients.append(np.zeros(layers[i+1]))

        self.activations.append(np.zeros(layers[-1]))
        
        if optimizer == 'adam':
            self.adam(self.train_X,self.train_Y)
        elif optimizer == 'sgd':
            self.sgd(self.train_X,self.train_Y)
        elif optimizer == 'momentum':
            self.momentum(self.train_X,self.train_Y)
        elif optimizer == 'nesterov':
            self.nesterov(self.train_X,self.train_Y)
        elif optimizer == 'nadam':
            self.nadam(self.train_X,self.train_Y)
        elif optimizer == 'rmsprop':
            self.rmsprop(self.train_X,self.train_Y)


    def sigmoid(self,activations):
        res = []
        for z in activations:
            if z>40:
                res.append(1.0)
            elif z<-40:
                res.append(0.0)
            else:
                res.append(1/(1+np.exp(-z)))
        return np.asarray(res)

    def tanh(self,activations):
        res = []
        for z in activations:
            if z>20:
                res.append(1.0)
            elif z<-20:
                res.append(-1.0)
            else:
                res.append((np.exp(z) - np.exp(-z))/(np.exp(z) + np.exp(-z)))
        return np.asarray(res)

    def relu(self,activations):
        res = []
        for i in activations:
            if i<= 0:
                res.append(0)
            else:
                res.append(i)
        return np.asarray(res)

    def softmax(self,activations):
        tot = 0
        for z in activations:
            tot += np.exp(z)
        return np.asarray([np.exp(z)/tot for z in activations])

    def onehot(self,y):
      y_onehot = np.zeros(self.output_dim)
      y_onehot[y] = 1
      return y_onehot


    def forward_propagation(self,x,y,weights,biases):
        self.activations[0] = x
        n = len(self.layers)
        for i in range(n-2):
            if self.activation_func == "sigmoid":
                self.activations[i+1] = self.sigmoid(np.matmul(weights[i].T,self.activations[i])+biases[i])
            elif self.activation_func == "tanh":
                self.activations[i+1] = self.tanh(np.matmul(weights[i].T,self.activations[i])+biases[i])
            elif self.activation_func == "relu":
                self.activations[i+1] = self.relu(np.matmul(weights[i].T,self.activations[i])+biases[i])

        self.activations[n-1] = self.softmax(np.matmul(weights[n-2].T,self.activations[n-2])+biases[n-2])  
        if self.loss == "cross_entropy":      
          return -(np.log2(self.activations[-1][y])) #Return cross entropy loss for single data point.
        elif self.loss == "squared_loss":
          y_onehot = self.onehot(y)
          return np.sum(np.square(self.activations[-1] - y_onehot))

    def grad_w(self,i):
        return np.matmul(self.activations[i].reshape((-1,1)),self.activation_gradients[i].reshape((1,-1)))


    def grad_b(self,i):
        return self.activation_gradients[i]


    def backward_propagation(self,x,y,weights,biases):
        y_onehot = self.onehot(y)
        n = len(self.layers)

        if self.loss == "cross_entropy": 
          self.activation_gradients[-1] =  -1*(y_onehot - self.activations[-1])
        elif self.loss == "squared_loss":
          temp_vec = 2 * (self.activations[-1] - y_onehot) * (self.activations[-1])
          for i in range(len(self.activations[-1])):
            self.activation_gradients[-1][i] = np.dot(temp_vec,(self.onehot(i) - np.asarray([self.activations[-1][i]]*self.output_dim)))
          
        for i in range(n-2,-1,-1):
            self.weights_gradients[i] += self.grad_w(i)
            self.biases_gradients[i] += self.grad_b(i)
            if i!=0:
                value = np.matmul(weights[i],self.activation_gradients[i])
                if self.activation_func == "sigmoid":
                    self.activation_gradients[i-1] = value * self.activations[i] * (1-self.activations[i])
                elif self.activation_func == "tanh":
                    self.activation_gradients[i-1] = value * (1-np.square(self.activations[i]))
                elif self.activation_func == "relu":
                    res = []
                    for k in self.activations[i]:
                        if k>0: res.append(1.0)
                        else: res.append(0.0)
                    res = np.asarray(res)
                    self.activation_gradients[i-1] = value * res

    def gradient_descent(self,train_X,train_Y):
        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0

            self.weights_gradients = [0*i for i in (self.weights_gradients)]
            self.biases_gradients = [0*i for i in (self.biases_gradients)]
            
            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,self.weights,self.biases)
                self.backward_propagation(x,y,self.weights,self.biases)

                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):
                        self.weights[j] -= self.learning_rate * self.weights_gradients[j]
                        self.biases[j] -= self.learning_rate * self.biases_gradients[j]
                    self.weights_gradients = [0*i for i in (self.weights_gradients)]
                    self.biases_gradients = [0*i for i in (self.biases_gradients)]
                index += 1 

            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)


    def sgd(self,train_X,train_Y):
        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0
            val_loss=0

            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,self.weights,self.biases)
                self.backward_propagation(x,y,self.weights,self.biases)

                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):
                        self.weights[j] -= self.learning_rate * self.weights_gradients[j]
                        self.biases[j] -= self.learning_rate * self.biases_gradients[j]
                    self.weights_gradients = [0*i for i in (self.weights_gradients)]
                    self.biases_gradients = [0*i for i in (self.biases_gradients)]
                index +=1

            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)

    
    def momentum(self,train_X,train_Y):
        prev_gradients_w = [0*i for i in (self.weights_gradients)]
        prev_gradients_b = [0*i for i in (self.biases_gradients)]

        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0
            val_loss=0

            self.weights_gradients = [0*i for i in (self.weights_gradients)]
            self.biases_gradients = [0*i for i in (self.biases_gradients)]

            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,self.weights,self.biases)
                self.backward_propagation(x,y,self.weights,self.biases)
                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):
                        v_w = (self.decay_rate * prev_gradients_w[j] + self.learning_rate * self.weights_gradients[j])
                        v_b = (self.decay_rate * prev_gradients_b[j] + self.learning_rate * self.biases_gradients[j])
                        self.weights[j] -= v_w
                        self.biases[j] -= v_b
                        prev_gradients_w[j] = v_w
                        prev_gradients_b[j] = v_b
                    self.weights_gradients = [0*i for i in (self.weights_gradients)]
                    self.biases_gradients = [0*i for i in (self.biases_gradients)]

                index +=1
            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)


    def nesterov(self,train_X,train_Y):
        prev_gradients_w = [0*i for i in (self.weights_gradients)]
        prev_gradients_b = [0*i for i in (self.biases_gradients)]

        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0
            val_loss=0

            weights = [self.weights[j] -  self.decay_rate * prev_gradients_w[j] for j in range(len(self.weights))]
            biases = [self.biases[j] -  self.decay_rate * prev_gradients_b[j] for j in range(len(self.biases))]

            self.weights_gradients = [0*j for j in (self.weights_gradients)]
            self.biases_gradients = [0*j for j in (self.biases_gradients)]
            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,weights,biases)
                self.backward_propagation(x,y,weights,biases)
                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):
                        prev_gradients_w[j] = self.decay_rate * prev_gradients_w[j] + self.learning_rate*self.weights_gradients[j] 
                                           
                        prev_gradients_b[j] = self.decay_rate * prev_gradients_b[j] + self.learning_rate*self.biases_gradients[j] 
                                        
                        self.weights[j] -= prev_gradients_w[j]
                        self.biases[j] -= prev_gradients_b[j]

                    weights = [self.weights[j] -  self.decay_rate * prev_gradients_w[j] for j in range(len(self.weights))]
                    biases = [self.biases[j] -  self.decay_rate * prev_gradients_b[j] for j in range(len(self.biases))]

                    self.weights_gradients = [0*j for j in (self.weights_gradients)]
                    self.biases_gradients = [0*j for j in (self.biases_gradients)]
                    
                index += 1
            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)


    def rmsprop(self,train_X,train_Y):
        prev_gradients_w = [0*i for i in (self.weights_gradients)]
        prev_gradients_b = [0*i for i in (self.biases_gradients)]
        eps = 1e-2

        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0
            val_loss=0

            self.weights_gradients = [0*i for i in (self.weights_gradients)]
            self.biases_gradients = [0*i for i in (self.biases_gradients)]

            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,self.weights,self.biases)
                self.backward_propagation(x,y,self.weights,self.biases)
                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):
                        v_w = (self.beta * prev_gradients_w[j] + (1-self.beta) * np.square(self.weights_gradients[j]))
                        v_b = (self.beta * prev_gradients_b[j] + (1-self.beta) * np.square(self.biases_gradients[j]))
                        self.weights[j] -= self.learning_rate * (self.weights_gradients[j] /(np.sqrt(v_w + eps)))
                        self.biases[j] -= self.learning_rate * (self.biases_gradients[j] /(np.sqrt(v_b + eps)))
                        prev_gradients_w[j] = v_w
                        prev_gradients_b[j] = v_b
                    self.weights_gradients = [0*i for i in (self.weights_gradients)]
                    self.biases_gradients = [0*i for i in (self.biases_gradients)]

                index +=1
            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)


    def adam(self,train_X,train_Y):
        m_prev_gradients_w = [0*i for i in (self.weights_gradients)]
        m_prev_gradients_b = [0*i for i in (self.biases_gradients)]
        v_prev_gradients_w = [0*i for i in (self.weights_gradients)]
        v_prev_gradients_b = [0*i for i in (self.biases_gradients)]

        iter = 1

        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0
            val_loss=0
            eps = 1e-2
            self.weights_gradients = [0*i for i in (self.weights_gradients)]
            self.biases_gradients = [0*i for i in (self.biases_gradients)]

            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,self.weights,self.biases)
                self.backward_propagation(x,y,self.weights,self.biases)
                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):
                        m_w = (self.beta1 * m_prev_gradients_w[j] + (1-self.beta1) * self.weights_gradients[j])
                        m_b = (self.beta1 * m_prev_gradients_b[j] + (1-self.beta1) * self.biases_gradients[j])
                        v_w = (self.beta2 * v_prev_gradients_w[j] + (1-self.beta2) * np.square(self.weights_gradients[j]))
                        v_b = (self.beta2 * v_prev_gradients_b[j] + (1-self.beta2) * np.square(self.biases_gradients[j]))

                        m_hat_w = (m_w)/(1-(self.beta1)**iter) 
                        m_hat_b = (m_b)/(1-(self.beta1)**iter) 

                        v_hat_w = (v_w)/(1-(self.beta2)**iter) 
                        v_hat_b = (v_b)/(1-(self.beta2)**iter)

                        self.weights[j] -= self.learning_rate * (m_hat_w/(np.sqrt(v_hat_w + eps)))
                        self.biases[j] -= self.learning_rate * (m_hat_b/(np.sqrt(v_hat_b + eps)))

                        m_prev_gradients_w[j] = m_w
                        m_prev_gradients_b[j] = m_b
                        v_prev_gradients_w[j] = v_w
                        v_prev_gradients_b[j] = v_b

                    self.weights_gradients = [0*i for i in (self.weights_gradients)]
                    self.biases_gradients = [0*i for i in (self.biases_gradients)]
                    iter += 1

                index +=1
            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)

    def nadam(self,train_X,train_Y):
        m_prev_gradients_w = [0*i for i in (self.weights_gradients)]
        m_prev_gradients_b = [0*i for i in (self.biases_gradients)]
        v_prev_gradients_w = [0*i for i in (self.weights_gradients)]
        v_prev_gradients_b = [0*i for i in (self.biases_gradients)]

        iter = 1

        for i in range(self.epochs):
            print('Epoch---',i+1,end=" ")
            loss = 0
            val_loss=0
            eps = 1e-2
            self.weights_gradients = [0*i for i in (self.weights_gradients)]
            self.biases_gradients = [0*i for i in (self.biases_gradients)]

            index = 1
            for x,y in zip(train_X,train_Y):
                x = x.ravel()
                loss += self.forward_propagation(x,y,self.weights,self.biases)
                self.backward_propagation(x,y,self.weights,self.biases)
                if index % self.batch == 0 or index == train_X.shape[0]:
                    for j in range(len(self.weights)):

                        m_w = (self.beta1 * m_prev_gradients_w[j] + (1-self.beta1) * self.weights_gradients[j])
                        m_b = (self.beta1 * m_prev_gradients_b[j] + (1-self.beta1) * self.biases_gradients[j])
                        v_w = (self.beta2 * v_prev_gradients_w[j] + (1-self.beta2) * np.square(self.weights_gradients[j]))
                        v_b = (self.beta2 * v_prev_gradients_b[j] + (1-self.beta2) * np.square(self.biases_gradients[j]))

                        m_hat_w = (m_w)/(1-(self.beta1)**iter) 
                        m_hat_b = (m_b)/(1-(self.beta1)**iter) 

                        v_hat_w = (v_w)/(1-(self.beta2)**iter) 
                        v_hat_b = (v_b)/(1-(self.beta2)**iter)

                        m_dash_w = self.beta1 * m_hat_w + (1-self.beta1) * self.weights_gradients[j]
                        m_dash_b = self.beta1 * m_hat_b + (1-self.beta1) * self.biases_gradients[j]

                        self.weights[j] -= self.learning_rate * (m_dash_w/(np.sqrt(v_hat_w + eps)))
                        self.biases[j] -= self.learning_rate * (m_dash_b/(np.sqrt(v_hat_b + eps)))

                        m_prev_gradients_w[j] = m_w
                        m_prev_gradients_b[j] = m_b
                        v_prev_gradients_w[j] = v_w
                        v_prev_gradients_b[j] = v_b

                    self.weights_gradients = [0*i for i in (self.weights_gradients)]
                    self.biases_gradients = [0*i for i in (self.biases_gradients)]
                    iter += 1

                index +=1

            for x,y in zip(self.x_cv,self.y_cv):
               x=x.ravel()
               val_loss+=self.forward_propagation(x,y,self.weights,self.biases)

            acc=round(self.calculate_accuracy(train_X,train_Y),3)
            val_acc=round(self.calculate_accuracy(self.x_cv,self.y_cv),3)
            # wandb.log({'train_loss':loss/train_X.shape[0],'train_accuracy':acc,'val_loss':val_loss/self.x_cv.shape[0],'val_accuarcy':val_acc})
            print('  loss = ',loss/train_X.shape[0],'  accuracy = ',acc,'   validation loss= ',val_loss/self.x_cv.shape[0],'  validation accuaracy= ',val_acc)


    def calculate_accuracy(self,X,Y):
        count = 0
        for i in range(len(X)):
            if self.predict(X[i]) == Y[i]:
                count+=1
        return count/len(X)


    def predict(self,x):
        x = x.ravel()
        self.activations[0] = x
        n = len(self.layers)
        for i in range(n-2):
            if self.activation_func == "sigmoid":
                self.activations[i+1] = self.sigmoid(np.matmul(self.weights[i].T,self.activations[i])+self.biases[i])
            elif self.activation_func == "tanh":
                self.activations[i+1] = self.tanh(np.matmul(self.weights[i].T,self.activations[i])+self.biases[i])
            elif self.activation_func == "relu":
                self.activations[i+1] = self.relu(np.matmul(self.weights[i].T,self.activations[i])+self.biases[i])

        self.activations[n-1] = self.softmax(np.matmul(self.weights[n-2].T,self.activations[n-2])+self.biases[n-2])

        return np.argmax(self.activations[-1])

nn = Neural_network(train_X,train_Y,784,64,2,10,learning_rate=2e-3,batch_size= 64,epochs=4,
                    activation_func="tanh",optimizer="nadam",weight_init="xavier",decay_rate=0.1,loss="cross_entropy")

print("The test accuracy is:",nn.calculate_accuracy(test_X,test_Y))

n = Neural_network(train_X,train_Y,784,64,2,10,learning_rate=5e-3,batch_size= 32,epochs=7,
                    activation_func="relu",optimizer="adam",weight_init="xavier",decay_rate=0.1,loss="cross_entropy")

print("The test accuracy is:",nn.calculate_accuracy(test_X,test_Y))

nn = Neural_network(train_X,train_Y,784,16,3,10,learning_rate=6e-3,batch_size= 32,epochs=5,
                    activation_func="sigmoid",optimizer="rmsprop",weight_init="random",decay_rate=0.1,loss="cross_entropy")

print("The test accuracy is:",nn.calculate_accuracy(test_X,test_Y))