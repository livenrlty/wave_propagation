import torch
import torch.nn as nn

def double_conv(in_channels, out_channels):
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, 3, padding=1),
        nn.ReLU(inplace=True),
        nn.Conv2d(out_channels, out_channels, 3, padding=1),
        nn.ReLU(inplace=True)
    )


class UNet(nn.Module):

    def __init__(self, num_input_frames, num_output_frames):
        super().__init__()
        self.num_input_frames = num_input_frames
        self.num_output_frames = num_output_frames
        self.dconv_down1 = double_conv(num_input_frames, 64)
        self.dconv_down2 = double_conv(64, 128)
        self.dconv_down3 = double_conv(128, 256)
        self.dconv_down4 = double_conv(256, 512)

        self.maxpool = nn.MaxPool2d(2)
        # self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

        self.upsample = lambda x: torch.nn.functional.interpolate(x, mode='bilinear', scale_factor=2, align_corners=True)

        self.dconv_up3 = double_conv(256 + 512, 256)
        self.dconv_up2 = double_conv(128 + 256, 128)
        self.dconv_up1 = double_conv(128 + 64, 64)

        self.conv_last = nn.Conv2d(64, num_output_frames, 1)


    def forward(self, x):
        conv1 = self.dconv_down1(x)
        x = self.maxpool(conv1)

        conv2 = self.dconv_down2(x)
        x = self.maxpool(conv2)

        conv3 = self.dconv_down3(x)
        x = self.maxpool(conv3)

        x = self.dconv_down4(x)

        x = self.upsample(x)
        x = torch.cat([x, conv3], dim=1)

        x = self.dconv_up3(x)
        x = self.upsample(x)
        x = torch.cat([x, conv2], dim=1)

        x = self.dconv_up2(x)
        x = self.upsample(x)
        x = torch.cat([x, conv1], dim=1)

        x = self.dconv_up1(x)

        out = self.conv_last(x)

        return out

    def get_future_frames(self, input_frames, num_total_output_frames, belated):
        output_frames = self(input_frames)
        num_input_frames = self.get_num_input_frames()

        while output_frames.size(1) < num_total_output_frames:
            if output_frames.size(1) < num_input_frames:
                keep_from_input = num_input_frames - output_frames.size(1)
                input_frames = torch.cat((input_frames[:, -keep_from_input:, :, :], output_frames), dim=1)
            else:
                input_frames = output_frames[:, -num_input_frames:, :, :].clone()
            output_frames = torch.cat((output_frames, self(input_frames)), dim=1)
        return output_frames[:, :num_total_output_frames, :, :]

    def get_num_input_frames(self):
        return self.num_input_frames

    def get_num_output_frames(self):
        return self.num_output_frames