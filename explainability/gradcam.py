import torch
import torch.nn.functional as F


class GradCAM:

    def __init__(self, model, target_layer):

        self.model = model
        self.target_layer = target_layer

        self.activations = None
        self.gradients = None

        self.forward_handle = target_layer.register_forward_hook(
            self._forward_hook
        )

        self.backward_handle = target_layer.register_full_backward_hook(
            self._backward_hook
        )

    def _forward_hook(self, module, inputs, output):

        self.activations = output

    def _backward_hook(self, module, grad_input, grad_output):

        self.gradients = grad_output[0]

    def generate(self, image, target_class=None):

        self.model.zero_grad()

        output = self.model(image)

        # Binary classifier:
        # positive logit corresponds to HGG.
        if target_class is None:
            target = output

        elif target_class == 1:
            target = output

        else:
            target = -output

        target.backward(
            retain_graph=True
        )

        if self.activations is None:
            raise RuntimeError(
                "Grad-CAM activations were not captured."
            )

        if self.gradients is None:
            raise RuntimeError(
                "Grad-CAM gradients were not captured."
            )

        # Global-average-pool the gradients
        # across spatial dimensions.
        weights = self.gradients.mean(
            dim=(2, 3),
            keepdim=True
        )

        # Weighted combination of feature maps.
        cam = (
            weights * self.activations
        ).sum(
            dim=1,
            keepdim=True
        )

        # Keep only positive contributions.
        cam = F.relu(cam)

        # Resize to the original MRI dimensions.
        cam = F.interpolate(
            cam,
            size=image.shape[-2:],
            mode="bilinear",
            align_corners=False
        )

        # Normalize each heatmap to [0, 1].
        cam_min = cam.amin(
            dim=(2, 3),
            keepdim=True
        )

        cam_max = cam.amax(
            dim=(2, 3),
            keepdim=True
        )

        cam = (
            cam - cam_min
        ) / (
            cam_max - cam_min + 1e-8
        )

        return cam.detach()

    def remove_hooks(self):

        self.forward_handle.remove()
        self.backward_handle.remove()
