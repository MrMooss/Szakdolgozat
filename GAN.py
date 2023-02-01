from keras.models import Sequential
from keras import Model
from keras.layers import *
from keras.applications.vgg19 import VGG19

counter = 0

def res_block(input):
    res = Conv2D(64, (3, 3), padding="same")(input)
    res = BatchNormalization(momentum=0.5)(res)
    res = PReLU(shared_axes=[1, 2])(res)
    res = Conv2D(64, (3, 3), padding="same")(res)
    res = BatchNormalization(momentum=0.5)(res)

    return add([input, res])


def up_block(input):
    up = Conv2D(256, (3, 3), padding="same")(input)
    up = UpSampling2D(size=2)(up)
    up = PReLU(shared_axes=[1, 2])(up)

    return up


def create_gen(gen_ip, num_res_block):
    layers = Conv2D(64, (9, 9), padding="same")(gen_ip)
    layers = PReLU(shared_axes=[1, 2])(layers)

    temp = layers

    for i in range(num_res_block):
        layers = res_block(layers)

    layers = Conv2D(64, (3, 3), padding="same")(layers)
    layers = BatchNormalization(momentum=0.5)(layers)
    layers = add([layers,temp])

    layers = up_block(layers)
    layers = up_block(layers)

    op = Conv2D(3, (9,9), padding="same")(layers)

    return Model(inputs=gen_ip, outputs=op, name=str(++counter))


def dic_block(input, filter, strides=1, bn=True):
    layer = Conv2D(filter, (3, 3), strides=strides, padding="same")(input)
    if bn:
        layer = BatchNormalization(momentum=0.8)(layer)
    layer = LeakyReLU(alpha=0.2)(layer)
    return layer


def discriminator(disc_input):
    df = 64

    d1 = dic_block(disc_input, df, bn=False)
    d2 = dic_block(d1, df, strides=2)
    d3 = dic_block(d2, df * 2)
    d4 = dic_block(d3, df * 2, strides=2)
    d5 = dic_block(d4, df * 4)
    d6 = dic_block(d5, df * 4, strides=2)
    d7 = dic_block(d6, df * 8)
    d8 = dic_block(d7, df * 8, strides=2)
    d8_5 = Flatten()(d8)
    d9 = Dense(df * 16)(d8_5)
    d10 = LeakyReLU(alpha=0.2)(d9)
    validity = Dense(1, activation='sigmoid')(d10)

    return Model(disc_input, validity, name='1')


def build_vgg(hr_shape):
    vgg = VGG19(weights="imagenet", include_top=False, input_shape=hr_shape)

    return Model(inputs=vgg.inputs, outputs=vgg.layers[9].output, name=str(++counter))


def createGan(gen, disc, vgg, lr_input, hr_input):
    generator_image = gen(lr_input)
    generator_features = vgg(generator_image)
    disc.trainable = False
    val = disc(generator_image)

    return Model(inputs=[lr_input, hr_input], outputs=[val, generator_features], name=str(++counter))
