import matplotlib.pyplot as plt
import pandas as pd
import shutil
import numpy as np 
import pickle

def save_plot_history(history, save_path,split_num=0):
    
    historyInDrivePath = save_path + '_split_'+ str(split_num) +'_history.csv'
    pd.DataFrame(history).to_csv(historyInDrivePath) #gdrive
    pd.DataFrame(history).to_csv('split_'+str(split_num)+'_history.csv')  #local

    print('plotting and saving train test graphs...')
    #print(history.keys())
    # summarize history for accuracy
    plt.figure(figsize=(10, 6))
    plt.plot(history['acc'])
    plt.plot(history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.grid(True)
    plt.savefig('split_'+str(split_num)+'_accuracy.png',bbox_inches='tight') #local
    plt.savefig(save_path+'accuracy.png',bbox_inches='tight') #gdrive
    

    
    # summarize history for loss
    plt.figure(figsize=(10, 6))
    plt.plot(history['loss'])
    plt.plot(history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.grid(True)
    plt.savefig('split_'+str(split_num)+'_loss.png',bbox_inches='tight')  #local
    plt.savefig(save_path+'loss.png',bbox_inches='tight')  #gdrive

def save_history_as_pickle(file_, path_, dataset_):
    local_path = str(dataset_) + '_historyOnEachSplit.pickle'
    drive_path = path_ + '_historyOnEachSplit.pickle'
    try:
        with open(local_path, 'wb') as fp:
            pickle.dump(file_, fp)
        print('saved', local_path)
        with open(drive_path, 'wb') as fp:
            pickle.dump(drive_path, fp)
        print('saved', drive_path)
    except Exception as e:
        print(e)

def evaluate_accuracy_method1(file_):
    test_acc = []
    for history in file_:
        test_acc_fold = history['val_acc']
        test_acc_fold = np.array(test_acc_fold,dtype=np.float32)
        test_acc.append(test_acc_fold)
    test_acc =  np.array(test_acc)
    mean_acc =  np.mean(test_acc,axis=0)
    print('--------------------------------------------')
    print('accuracy_evaluation_method_1 : ')
    epoch_index = np.argmax(mean_acc)
    max_mean_acc = np.max(mean_acc)
    print( 'max mean accuracy :',max_mean_acc, '_epoch :', (epoch_index + 1) )
    start_index = max( epoch_index-10 , 0 )
    end_index = min( epoch_index+10 , np.size(mean_acc)-1 )
    hundred_acc = test_acc[:,start_index:end_index]
    print('final accuracy :',np.mean(hundred_acc),'±',np.std(hundred_acc))
    print('--------------------------------------------')

def evaluate_accuracy_method2(file_):
    test_acc = []
    for history in file_:
        test_acc_fold = history['val_acc']
        test_acc_fold = np.array(test_acc_fold,dtype=np.float32)
        test_acc.append(test_acc_fold)
    test_acc = np.array(test_acc)
    print('--------------------------------------------')
    print("accuracy_evaluation_method_2 : (Sudhakaran's method)")
    max_test_acc_fold = np.max(test_acc,axis=1)
    print('max accuracy per fold : ',max_test_acc_fold)
    print('final accuracy :',np.mean(max_test_acc_fold),'±',np.std(max_test_acc_fold))
    print('--------------------------------------------')




def remove_data(dataset):
    print('removing the data folders...')
    shutil.rmtree('/{}/videos'.format(dataset))
    shutil.rmtree('/{}/processed'.format(dataset))
    print('work on split number',split_num,'done!')