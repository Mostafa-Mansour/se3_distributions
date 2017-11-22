import torch
import torch.nn as nn
import torch.utils.model_zoo as model_zoo


__all__ = ['AlexNet', 'alexnet']


model_urls = {
    'alexnet': 'https://download.pytorch.org/models/alexnet-owt-4df8aa71.pth',
}

#class LRN(nn.Module):
#    def __init__(self, local_size=1, alpha=1.0, beta=0.75, ACROSS_CHANNELS=True):
#        super(LRN, self).__init__()
#        self.ACROSS_CHANNELS = ACROSS_CHANNELS
#        if ACROSS_CHANNELS:
#            self.average=nn.AvgPool3d(kernel_size=(local_size, 1, 1),
#                                      stride=1,
#                                      padding=(int((local_size-1.0)/2), 0, 0))
#        else:
#            self.average=nn.AvgPool2d(kernel_size=local_size,
#                                      stride=1,
#                                      padding=int((local_size-1.0)/2))
#        self.alpha = alpha
#        self.beta = beta
#
#
#    def forward(self, x):
#        if self.ACROSS_CHANNELS:
#            div = x.pow(2).unsqueeze(1)
#            div = self.average(div).squeeze(1)
#            div = div.mul(self.alpha).add(1.0).pow(self.beta)
#        else:
#            div = x.pow(2)
#            div = self.average(div)
#            div = div.mul(self.alpha).add(1.0).pow(self.beta)
#        x = x.div(div)
#        return x


class GenPoseNet(nn.Module):

    def __init__(self):
        super(GenPoseNet, self).__init__()
        self.features_euler = nn.Sequential(
            nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2), #conv1
            nn.ReLU(inplace=True),                                 #relu1
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool1
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm1
            nn.Conv2d(96, 256, kernel_size=5, padding=2),          #conv2
            nn.ReLU(inplace=True),                                 #relu2
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool2
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm2
            nn.Conv2d(256, 384, kernel_size=3, padding=1),         #conv3
            nn.ReLU(inplace=True),                                 #relu3
            nn.Conv2d(384, 384, kernel_size=3, padding=1),         #conv4
            nn.ReLU(inplace=True),                                 #relu4
            nn.Conv2d(384, 256, kernel_size=3, padding=1),         #conv5
            nn.ReLU(inplace=True),                                 #relu5
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool5
        )

        self.features_quat = nn.Sequential(
            nn.Conv2d(3, 96, kernel_size=11, stride=4, padding=2), #conv1
            nn.ReLU(inplace=True),                                 #relu1
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool1
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm1
            nn.Conv2d(96, 256, kernel_size=5, padding=2),          #conv2
            nn.ReLU(inplace=True),                                 #relu2
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool2
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm2
            nn.Conv2d(256, 384, kernel_size=3, padding=1),         #conv3
            nn.ReLU(inplace=True),                                 #relu3
            nn.Conv2d(384, 384, kernel_size=3, padding=1),         #conv4
            nn.ReLU(inplace=True),                                 #relu4
            nn.Conv2d(384, 256, kernel_size=3, padding=1),         #conv5
            nn.ReLU(inplace=True),                                 #relu5
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool5
        )

        self.euler_linear = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 6 * 6 * 2, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
        )

        self.azimuth_linear = nn.Linear(4096, 360)
        self.elevation_linear = nn.Linear(4096, 360)
        self.tilt_linear = nn.Linear(4096, 360)
        
        self.quaternion_linear = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 6 * 6 * 2, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 4),
        )

    def forward_quat(self, origin, query):
        origin = self.features_quat(origin)
        query = self.features_quat(query)
        origin = origin.view(origin.size(0), 256 * 6 * 6)
        query = query.view(query.size(0), 256 * 6 * 6)        

        x = self.quaternion_linear(torch.cat((origin, query), dim=1))
        return x
        
    def forward_euler(self, origin, query):
        origin = self.features_euler(origin)
        query = self.features_euler(query)
        origin = origin.view(origin.size(0), 256 * 6 * 6)
        query = query.view(query.size(0), 256 * 6 * 6)        
        
        x = self.euler_linear(torch.cat((origin, query), dim=1))

        azimuth = self.azimuth_linear(x)
        elevation = self.elevation_linear(x)
        tilt = self.tilt_linear(x)
        return azimuth, elevation, tilt

    def forward(self, origin, query):
        quat = self.forward_quat(origin, query)
        azimuth, elevation, tilt = self.forward_euler(origin, query)
        return quat, azimuth, elevation, tilt

class GenPoseNetStacked(nn.Module):

    def __init__(self):
        super(GenPoseNet, self).__init__()
        self.features_euler = nn.Sequential(
            nn.Conv2d(6, 192, kernel_size=11, stride=4, padding=2), #conv1
            nn.ReLU(inplace=True),                                 #relu1
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool1
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm1
            nn.Conv2d(192, 512, kernel_size=5, padding=2),          #conv2
            nn.ReLU(inplace=True),                                 #relu2
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool2
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm2
            nn.Conv2d(512, 768, kernel_size=3, padding=1),         #conv3
            nn.ReLU(inplace=True),                                 #relu3
            nn.Conv2d(768, 768, kernel_size=3, padding=1),         #conv4
            nn.ReLU(inplace=True),                                 #relu4
            nn.Conv2d(768, 512, kernel_size=3, padding=1),         #conv5
            nn.ReLU(inplace=True),                                 #relu5
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool5
        )

        self.features_quat = nn.Sequential(
            nn.Conv2d(6, 96, kernel_size=11, stride=4, padding=2), #conv1
            nn.ReLU(inplace=True),                                 #relu1
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool1
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm1
            nn.Conv2d(96, 512, kernel_size=5, padding=2),          #conv2
            nn.ReLU(inplace=True),                                 #relu2
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool2
            #LRN(local_size=5, alpha=0.0001, beta=0.75),            #norm2
            nn.Conv2d(512, 768, kernel_size=3, padding=1),         #conv3
            nn.ReLU(inplace=True),                                 #relu3
            nn.Conv2d(768, 768, kernel_size=3, padding=1),         #conv4
            nn.ReLU(inplace=True),                                 #relu4
            nn.Conv2d(768, 512, kernel_size=3, padding=1),         #conv5
            nn.ReLU(inplace=True),                                 #relu5
            nn.MaxPool2d(kernel_size=3, stride=2),                 #pool5
        )

        self.euler_linear = nn.Sequential(
            nn.Dropout(),
            nn.Linear(512 * 6 * 6 * 2, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
        )

        self.azimuth_linear = nn.Linear(4096, 360)
        self.elevation_linear = nn.Linear(4096, 360)
        self.tilt_linear = nn.Linear(4096, 360)
        
        self.quaternion_linear = nn.Sequential(
            nn.Dropout(),
            nn.Linear(512 * 6 * 6 * 2, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 4),
        )

    def forward_quat(self, origin, query):
        features = self.features_euler(torch.cat((origin, query), dim=1))
        features = features.view(features.size(0), 256 * 6 * 6)
        x = self.quaternion_linear(torch.cat((origin, query), dim=1))
        return x
        
    def forward_euler(self, origin, query):
        features = self.features_quat(torch.cat((origin, query), dim=1))
        features = features.view(features.size(0), 256 * 6 * 6)        
        x = self.euler_linear(features)

        azimuth = self.azimuth_linear(x)
        elevation = self.elevation_linear(x)
        tilt = self.tilt_linear(x)
        return azimuth, elevation, tilt

    def forward(self, origin, query):
        quat = self.forward_quat(origin, query)
        azimuth, elevation, tilt = self.forward_euler(origin, query)
        return quat, azimuth, elevation, tilt


def gen_pose_net(pretrained=False, **kwargs):
    r"""AlexNet model architecture from the
    `"One weird trick..." <https://arxiv.org/abs/1404.5997>`_ paper.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = GenPoseNet(**kwargs)
    if pretrained:
        pretrained_dict = model_zoo.load_url(model_urls['alexnet'])
        model_dict = model.state_dict()
        pretrained_dict = {k: v for k, v in pretrained_dict.items() if k in model_dict}
        model_dict.update(pretrained_dict) 
        model.load_state_dict(model_dict)
        
    return model
    
    
def gen_pose_net_stacked(pretrained=False, **kwargs):
    r"""AlexNet model architecture from the
    `"One weird trick..." <https://arxiv.org/abs/1404.5997>`_ paper.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
    """
    model = GenPoseNet(**kwargs)
        
    return model