from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        
        # Initialize wight
        self.params['W1'] = weight_scale * np.random.randn(input_dim, hidden_dim)
        self.params['W2'] = weight_scale * np.random.randn(hidden_dim, num_classes)
        
        # Initialize bias
        self.params['b1'] = np.zeros(hidden_dim)
        self.params['b2'] = np.zeros(num_classes)
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        
        # Unpack variables from the params dictionary
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        
        # Compute the forward pass
        # Forward into first layer
        hidden_layer, cache_hidden_layer = affine_relu_forward(X, W1, b1)
        # Forward into second layer
        scores, cache_scores = affine_forward(hidden_layer, W2, b2)
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        
        # Compute loss & gradient of scores
        data_loss, dscores = softmax_loss(scores, y)
        reg_loss = 0.5 * self.reg * np.sum(W1**2)
        reg_loss += 0.5 * self.reg * np.sum(W2**2)
        loss = data_loss + reg_loss

        # Backprop into second layer
        dx1, dW2, db2 = affine_backward(dscores, cache_scores)
        dW2 += self.reg * W2

        # Backprop into first layer
        dx, dW1, db1 = affine_relu_backward(dx1, cache_hidden_layer)
        dW1 += self.reg * W1
    
        # assign gradient class
        grads['W2'] = dW2
        grads['b2'] = db2
        grads['W1'] = dW1
        grads['b1'] = db1
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch/layer normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch/layer normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=1, normalization=None, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=1 then
          the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
          are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.normalization = normalization
        self.use_dropout = dropout != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        
        # iterate every layer
        for i in range(1, self.num_layers+1):
            
            # determine input/output dimension of each layer
            layer_input_dim = input_dim if i == 1 else hidden_dims[i-2]
            layer_output_dim = num_classes if i==self.num_layers else hidden_dims[i-1]
            
            # initialize parameters of Weight & bias
            self.params['W'+str(i)] = np.random.normal(0, weight_scale, (layer_input_dim, layer_output_dim))
            self.params['b'+str(i)] = np.zeros(layer_output_dim)
            
            # initialize parameters of Weight & bias
            if normalization!=None and i!=self.num_layers:
                self.params['beta'+str(i)]=np.zeros(layer_output_dim)
                self.params['gamma'+str(i)]=np.ones(layer_output_dim)
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        self.ln_params = []
        if self.normalization=='batchnorm':
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]
        if self.normalization=='layernorm':
            self.ln_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.normalization=='batchnorm':
            for bn_param in self.bn_params:
                bn_param['mode'] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        
        # initialize
        current_input = X 
        affine_relu_cache={}
        affine_bn_relu_cache={}
        dropout_cache={}
        caches = {}

        # iterate each layer (except last layer)
        for i in range(1, self.num_layers):
            
            if self.normalization == None:
                current_input, affine_relu_cache[i] = affine_relu_forward(current_input, 
                                                                          self.params['W'+str(i)], 
                                                                          self.params['b'+str(i)])
            elif self.normalization == 'batchnorm':  
                # affine -> batch norm -> relu
                fc_out, fc_cache = affine_forward(current_input, self.params['W'+str(i)], self.params['b'+str(i)])
                bn_out, bn_cache = batchnorm_forward(fc_out, \
                                                     self.params['gamma'+str(i)], \
                                                     self.params['beta'+str(i)], \
                                                     self.bn_params[i-1])
                current_input, relu_cache = relu_forward(bn_out)
                caches[i] = (fc_cache, bn_cache, relu_cache)
                
            elif self.normalization == 'layernorm':
                # affine -> layer norm -> relu
                fc_out, fc_cache = affine_forward(current_input, self.params['W'+str(i)], self.params['b'+str(i)])
                ln_out, ln_cache = layernorm_forward(fc_out, \
                                                     self.params['gamma'+str(i)], \
                                                     self.params['beta'+str(i)], \
                                                     self.ln_params[i-1])
                current_input, relu_cache = relu_forward(ln_out)
                caches[i] = (fc_cache, ln_cache, relu_cache)
                
            if self.use_dropout:
                current_input, dropout_cache[i] = dropout_forward(current_input, self.dropout_param)  
    
    
        # Last affine layer
        affine_out, affine_cache = affine_forward(current_input, 
                                                  self.params['W'+str(self.num_layers)], 
                                                  self.params['b'+str(self.num_layers)])
        scores = affine_out        
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        
        # caluculate loss
        loss, dscores = softmax_loss(scores, y)
        
        # add reg for loss
        loss += 0.5 * self.reg*(np.sum(self.params['W'+str(self.num_layers)]**2))

        # calculate gradient of last layer
        affine_dx, affine_dw, affine_db = affine_backward(dscores, affine_cache)
        grads['W'+str(self.num_layers)] = affine_dw + self.reg * self.params['W'+str(self.num_layers)]
        grads['b'+str(self.num_layers)] = affine_db

        # calculate gradient of each layer (except last layer)
        for i in range(self.num_layers-1,0,-1):
            if self.use_dropout:
                affine_dx = dropout_backward(affine_dx, dropout_cache[i])
    
            if self.normalization == None:       
                affine_dx, affine_dw, affine_db = affine_relu_backward(affine_dx, affine_relu_cache[i])
    
            else:
                # Dropout backward except the last layer (before relu backward)
                if self.normalization == 'batchnorm':
                    # drelu -> dbatchnorm -> daffine
                    fc_cache, bn_cache, relu_cache = caches[i]
                    dbn_out = relu_backward(affine_dx, relu_cache)
                    dfc_out, grads['gamma'+str(i)], grads['beta'+str(i)] = batchnorm_backward(dbn_out, bn_cache)
                    affine_dx, affine_dw, affine_db = affine_backward(dfc_out, fc_cache)
                    
                if self.normalization == 'layernorm':
                    # drelu -> dlayernorm -> daffine
                    fc_cache, ln_cache, relu_cache = caches[i]
                    dln_out = relu_backward(affine_dx, relu_cache)
                    dfc_out, grads['gamma'+str(i)], grads['beta'+str(i)] = layernorm_backward(dln_out, ln_cache)
                    affine_dx, affine_dw, affine_db = affine_backward(dfc_out, fc_cache)
            
            grads['W'+str(i)] = affine_dw + self.reg * self.params['W'+str(i)]
            grads['b'+str(i)] = affine_db
            
            # add reg for loss
            loss += 0.5 * self.reg*(np.sum(self.params['W'+str(i)]**2)) 
        
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads
