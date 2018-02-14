import numpy as np
from hmmlearn import hmm
import types



class markovmodel:
    #transmat: None
    def __init__(self, transmat = None, startprob = None):
        self.transmat = transmat
        self.startprob = startprob
    # It assumes the state number starts from 0
    def fit(self, X):
        ns = max([max(items) for items in X]) + 1
        self.transmat  = np.zeros([ns, ns])
        self.startprob = np.zeros([ns])
        for items in X:
            n = len(items)
            self.startprob[items[0]] += 1
            for i in range(n-1):
                self.transmat[items[i], items[i+1]] += 1
        self.startprob = self.startprob / sum(self.startprob)
        n = self.transmat.shape[0]
        d = np.sum(self.transmat, axis=1)
        for i in range(n):
            if d[i] == 0:
                self.transmat[i,:] = 1.0 / n
        d[d == 0] = 1
        self.transmat = self.transmat * np.transpose(np.outer(np.ones([ns,1]), 1./d))

    def predict(self, obs, steps):
        pred = []
        n = len(obs)
        if len(obs) > 0:
            s = obs[-1]
        else:
            s = np.argmax(np.random.multinomial(1, self.startprob.tolist(), size = 1))
        for i in range(steps):
            s1 = np.random.multinomial(1, self.transmat[s,:].tolist(), size = 1)
            pred.append(np.argmax(s1))
            s = np.argmax(s1)
        return pred


def hmm_predict_further_states(ghmm, obs, steps):
    y = ghmm.predict(obs)
    mm = markovmodel(ghmm.transmat_, ghmm.startprob_)
    return mm.predict([y[-1]], steps)

def hmm_predict_future_features(ghmm, obs, steps):
    y = ghmm.predict(obs)
    pred = []
    mm = markovmodel(ghmm.transmat_, ghmm.startprob_)
    sts = mm.predict([], steps)
    for s in sts:
        mean = ghmm.means_[y[-1]]
        cov = ghmm.covars_[y[-1],:]
        x = np.random.multivariate_normal(mean,cov,1)
        pred.append(x[0].tolist())
    return pred


def estimate_parameters(X, y):
    mm = markovmodel()
    mm.fit(y)
    data = dict()
    for i in range(len(y)):
        for s, x in zip(y[i], X[i]):
            if s in data:
                data[s].append(x)
            else:
                data[s] = [x]
    ns = len(data.keys())
    means = np.array([[np.mean(data[s])] for s in range(ns)])
    covars = np.tile(np.identity(1), (ns, 1, 1))
    for s in range(ns):
        covars[s, 0] = np.std(data[s])
    return mm.startprob, mm.transmat, means, covars



label = {0: "New York City", 1: "Boston", 2: "Washington D.C."}
X = [[[800],  [400], [600]],
     [[550],  [900], [450]],
     [[750],  [650], [325]],
     [[425], [600],  [750]]]
y = [[0,     1,    2],
     [2,     0,    1],
     [0,     2,    1],
     [1,     2,    0]]



startprob, transmat, means, covars = estimate_parameters(X, y)
model = hmm.GaussianHMM(3, "full")
print (model)
model.startprob_ = startprob
model.transmat_ = transmat
model.means_  = means
model.covars_ = covars
for x in X:
    y = model.predict(x)
    print ([label[s] for s in y])



X = [[[450], [650]],
     [[850],  [500]]]

for x in X:
    y = model.predict(x)
    print ([label[s] for s in y])

x = [[450], [650]]
y = hmm_predict_further_states(model, x, 3)
print (label)
print (y)
print ([label[s] for s in y])


x = [[450], [650]]
cons = hmm_predict_future_features(model, x, 3)
print ([round(con[0], 2) for con in cons])

