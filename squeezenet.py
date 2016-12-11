import h5py
from keras.models import Model
from keras.layers import Input, Convolution2D, MaxPooling2D, Dropout, GlobalAveragePooling2D, merge

def FireModule(s_1x1, e_1x1, e_3x3, name):
    """
        Fire module for the SqueezeNet model. 
        Implements the expand layer, which has a mix of 1x1 and 3x3 filters, 
        by using two conv layers concatenated in the channel dimension. 

        Returns a callable function
    """
    def layer(x):
        squeeze = Convolution2D(s_1x1, 1, 1, activation='relu', name=name+'_squeeze')(x)
        expand_1x1 = Convolution2D(e_1x1, 1, 1, activation='relu', name=name+'_expand_1x1')(squeeze)
        expand_3x3 = Convolution2D(e_3x3, 3, 3, activation='relu', name=name+'_expand_3x3')(squeeze)
        expand_merge = merge([expand_1x1, expand_3x3], mode='concat', concat_axis=3, name=name+'_expand_merge')
        return expand_merge
    return layer
    


def SqueezeNet(nb_classes): 
    # Use input shape (227, 227, 3) instead of the (224, 224, 3) shape cited in the paper. 
    # This results in conv1 output shape = (None, 111, 111, 96), same as in the paper. 
    input_image = Input(shape=(227, 227, 3))
    conv1 = Convolution2D(96, 7, 7, activation='relu', subsample=(2, 2), name='conv1')(input_image)
    # maxpool1 output shape = (None, 55, 55, 96)
    maxpool1 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='maxpool1')(conv1)

    fire2 = FireModule(s_1x1=16, e_1x1=64, e_3x3=64, name='fire2')(maxpool1)
    fire3 = FireModule(s_1x1=16, e_1x1=64, e_3x3=64, name='fire3')(fire2)
    fire4 = FireModule(s_1x1=32, e_1x1=128, e_3x3=128, name='fire4')(fire3)
    maxpool4 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='maxpool4')(fire4)
    fire5 = FireModule(s_1x1=32, e_1x1=128, e_3x3=128, name='fire5')(maxpool4)
    fire6 = FireModule(s_1x1=48, e_1x1=192, e_3x3=192, name='fire6')(fire5)
    fire7 = FireModule(s_1x1=48, e_1x1=192, e_3x3=192, name='fire7')(fire6)
    fire8 = FireModule(s_1x1=64, e_1x1=256, e_3x3=256, name='fire8')(fire7)
    maxpool8 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2), name='maxpool8')(fire7)
    # Dropout after fire9 module.
    fire9 = FireModule(s_1x1=64, e_1x1=256, e_3x3=256, name='fire9')(maxpool8)
    fire9_dropout = Dropout(p=0.5, name='fire9_dropout')(fire9)

    conv10 = Convolution2D(nb_classes, 1, 1, activation='relu')(fire9_dropout)
    avgpool10 = GlobalAveragePooling2D(pool_size=(13, 13), strides=(1, 1), name='avgpool10')(conv10)
    softmax = Activation('softmax', name='softmax')(avgpool10)

    model = Model(input=input_image, output=[softmax])
    return model


