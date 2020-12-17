import numpy as np
from sklearn.linear_model import Perceptron

if __name__ == "__main__":
    X = np.array()
    Y = np.array()
    print(np.shape(X))
    print(np.shape(Y))

    clf = Perceptron(tol=1e-3, random_state=0)
    clf.fit(X,Y)
    print(clf.score(X,Y))
    test = np.array([0,0,0,0,0,0,0])
    test = test.reshape(1,-1)
    print(np.shape(test))
    print(clf.predict(test))
