
import numpy as np

import scipy.stats as sp
class GaussianMixModel(object):
    def __init__(self, X, k=3, Tl_prime_mean=0, initial_mu=[0,0,0], initial_sigma=[0,0,0]):
        # Algorithm can work for any number of columns in dataset
        X = np.asarray(X)
        self.m, self.n = X.shape
        self.data = X.copy()
        self.Tl_prime_mean = Tl_prime_mean
        self.initial_mu=initial_mu
        self.initial_sigma=initial_sigma
        print (np.mean(X))
        # number of mixtures
        self.k = k

    def _init(self):
        # init mixture means/sigmas
        self.mean_arr = np.asmatrix(np.random.random((self.k, self.n))+np.mean(self.data))
        self.mean_arr[0]=self.Tl_prime_mean
        self.mean_arr[1]=self.initial_mu[1] # -30
        self.mean_arr[2]=self.initial_mu[2] # 90
        # This is the place for initializations... and sigma!
        self.sigma_arr = np.array([np.asmatrix(np.identity(self.n)) for i in range(self.k)])
        self.sigma_arr[0][0][0]=self.initial_sigma[0]
        self.sigma_arr[1][0][0]=self.initial_sigma[1]
        self.sigma_arr[2][0][0]=self.initial_sigma[2]
        #self.sigma_arr[ # This is the place for initializations... and sigma!
        self.phi = np.ones(self.k)/self.k
        self.Z = np.asmatrix(np.empty((self.m, self.k), dtype=float))
        #Z Latent Variable giving probability of each point for each distribution

    def fit(self, tol=1e-4):
        # Algorithm will run unti max of log-likelihood is achieved
        self._init()
        num_iters = 0
        logl = 1
        previous_logl = -1000000000
        while(logl-previous_logl > tol):
            previous_logl = self.loglikelihood()
            self.e_step()
            self.m_step()
            num_iters += 1
            logl = self.loglikelihood()
            print('Iteration %d: log-likelihood is %.6f'%(num_iters, logl))
        print('Terminate at %d-th iteration:log-likelihood is %.6f'%(num_iters, logl))

    def loglikelihood(self):
        logl = 0
        for i in range(self.m):
            tmp = 0
            for j in range(self.k):
                #print(self.sigma_arr[j])
                tmp += sp.multivariate_normal.pdf(self.data[i, :],self.mean_arr[j, :].A1,self.sigma_arr[j, :]) * self.phi[j]
            logl += np.log(tmp)
        return logl




    def e_step(self):
        #Finding probability of each point belonging to each pdf and putting it in latent variable Z
        for i in range(self.m):
            den = 0
            for j in range(self.k):
                #print (self.data[i, :])
                num = sp.multivariate_normal.pdf(self.data[i, :],
                                                       self.mean_arr[j].A1,
                                                       self.sigma_arr[j]) *\
                      self.phi[j]
                den += num

                self.Z[i, j] = num
            self.Z[i, :] /= den
            assert self.Z[i, :].sum() - 1 < 1e-4  # 1e-4 Program stops if this condition is false

    def m_step(self):
        #Updating mean and variance
        for j in range(self.k):
            const = self.Z[:, j].sum()
            self.phi[j] = 1/self.m * const
            _mu_j = np.zeros(self.n)
            _sigma_j = np.zeros((self.n, self.n))
            for i in range(self.m):
                _mu_j += (self.data[i, :] * self.Z[i, j])
                _sigma_j += self.Z[i, j] * ((self.data[i, :] - self.mean_arr[j, :]).T * (self.data[i, :] - self.mean_arr[j, :]))

            #temp=self.mean_arr[0]
            self.mean_arr[j] = _mu_j / const
            self.mean_arr[0]=self.Tl_prime_mean # Do not adjust the mean of the 1st component.
            self.sigma_arr[j] = _sigma_j / const

        # print(self.mean_arr, self.sigma_arr)