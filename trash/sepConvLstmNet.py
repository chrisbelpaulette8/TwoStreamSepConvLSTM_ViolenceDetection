from tensorflow.keras import Input
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.layers import Dense, Flatten, Dropout, ZeroPadding3D, ConvLSTM2D, Reshape, BatchNormalization, Activation, Conv2D
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import TimeDistributed
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import ELU, ReLU, LeakyReLU, Lambda, Dense, Bidirectional, Conv3D, GlobalAveragePooling2D, Multiply, MaxPooling3D, MaxPooling2D, Concatenate, Add, AveragePooling2D 
from tensorflow.keras.initializers import glorot_uniform, he_normal
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2
from tensorflow.python.keras import backend as K
from customLayers import SepConvLSTM2D

def getModel(size=224, seq_len=32 , cnn_weight = 'imagenet',cnn_trainable = True, weight_decay = 0.00005, frame_diff_interval = 1):
    """parameters:
    size = height/width of each frame,
    seq_len = number of frames in each sequence,
    cnn_weight= None or 'imagenet'
       returns:
    model
    """
    
    frames_input = Input(shape=(seq_len, size, size, 3),name='frames_input')
    frames_diff_input = Input(shape=(seq_len - frame_diff_interval, size, size, 3),name='frames_diff_input')
    
    frames_cnn = MobileNetV2( input_shape = (size,size,3), alpha=0.35, weights='imagenet', include_top = False )
    frames_cnn = Model( inputs=[frames_cnn.layers[0].input],outputs=[frames_cnn.layers[-30].output] ) # taking only upto block 13

    print('> cnn_trainable : ', cnn_trainable)
    for layer in frames_cnn.layers:
        layer.trainable = cnn_trainable

    frames_diff_cnn = MobileNetV2( input_shape=(size,size,3), alpha=0.35, weights='imagenet', include_top = False )
    frames_diff_cnn = Model( inputs = [frames_diff_cnn.layers[0].input], outputs = [frames_diff_cnn.layers[-30].output] ) # taking only upto block 13
    
    print('> cnn_trainable : ', cnn_trainable)
    for layer in frames_diff_cnn.layers:
        layer.trainable = cnn_trainable

    frames_cnn = TimeDistributed( frames_cnn,name='frames_CNN' )( frames_input )
    frames_cnn = TimeDistributed( LeakyReLU(alpha=0.1), name='leaky_relu_1_' )( frames_cnn)
    frames_cnn = TimeDistributed( Dropout(0.25) ,name='dropout_1_' )(frames_cnn)

    frames_diff_cnn = TimeDistributed( frames_diff_cnn,name='frames_diff_CNN' )(frames_diff_input)
    frames_diff_cnn = TimeDistributed( LeakyReLU(alpha=0.1), name='leaky_relu_2_' )(frames_diff_cnn)
    frames_diff_cnn = TimeDistributed( Dropout(0.25) ,name='dropout_2_' )(frames_diff_cnn)

    lstm_dropout = 0.2
    frames_lstm = Bidirectional(SepConvLSTM2D( filters = 64, kernel_size=(3, 3), padding='same', return_sequences=False, dropout=lstm_dropout, recurrent_dropout=lstm_dropout, name='SepConvLSTM2D_1', kernel_regularizer=l2(weight_decay), recurrent_regularizer=l2(weight_decay)), name = 'Bidirectional_SepconvLSTM_Frames')(frames_cnn)
    frames_lstm = BatchNormalization( axis = -1 )(frames_lstm)

    frames_diff_lstm = Bidirectional(SepConvLSTM2D( filters = 64, kernel_size=(3, 3), padding='same', return_sequences=False, dropout=lstm_dropout, recurrent_dropout=lstm_dropout, name='SepConvLSTM2D_2', kernel_regularizer=l2(weight_decay), recurrent_regularizer=l2(weight_decay)), name = 'Bidirectional_SepconvLSTM_Frames_Diff')(frames_diff_cnn)
    frames_diff_lstm = BatchNormalization( axis = -1 )(frames_diff_lstm)

    lstm = Concatenate(axis=-1, name='concatenate_')([frames_lstm, frames_diff_lstm])
    
    lstm = MaxPooling2D((2,2) , name = 'max_pooling_')(lstm)
    
    x = Flatten()(lstm) 
  
    dense_dropout = 0.3
    x = Dense(128)(x)
    x = LeakyReLU(alpha=0.2)(x)
    x = Dropout(dense_dropout)(x)
    x = Dense(16)(x)
    x = LeakyReLU(alpha=0.1)(x)
    x = Dropout(dense_dropout)(x)
    predictions = Dense(1, activation='sigmoid')(x)
    
    model = Model(inputs=[frames_input, frames_diff_input], outputs=predictions)
    return model
