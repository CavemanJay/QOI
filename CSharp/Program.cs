// See https://aka.ms/new-console-template for more information
using CSharp;
using CSharp.Models;

var encoder = new Encoder(735, 588, ColorChannels.RGBA, ColorSpace.linear, @"C:\Users\User\Desktop\Programming\QOI\assets\monument.bin");
var output = encoder.Encode();

File.WriteAllBytes("./image.qoi", output);
