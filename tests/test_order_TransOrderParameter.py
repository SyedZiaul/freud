import numpy as np
import numpy.testing as npt
import freud
import unittest
import itertools
import util


class TestTransOrder(unittest.TestCase):
    def test_simple(self):
        box = freud.box.Box.square(10)

        # make a square grid
        xs = np.linspace(-box.Lx/2, box.Lx/2, 10, endpoint=False)
        positions = np.zeros((len(xs)**2, 3), dtype=np.float32)
        positions[:, :2] = np.array(list(itertools.product(xs, xs)),
                                    dtype=np.float32)

        rmax = 1.1
        n = 4
        trans = freud.order.TransOrderParameter(rmax, 4, n)
        # Test access
        with self.assertRaises(AttributeError):
            trans.num_particles
        with self.assertRaises(AttributeError):
            trans.box
        with self.assertRaises(AttributeError):
            trans.d_r

        test_set = util.makeRawQueryNlistTestSet(
            box, positions, positions, 'nearest', rmax, n, True)
        for ts in test_set:
            trans.compute(box, ts[0], nlist=ts[1])
            # Test access
            trans.num_particles
            trans.box
            trans.d_r

            npt.assert_allclose(trans.d_r, 0, atol=1e-6)

            self.assertEqual(box, trans.box)
            self.assertEqual(len(positions), trans.num_particles)

    def test_repr(self):
        trans = freud.order.TransOrderParameter(1.1, 4, 4)
        self.assertEqual(str(trans), str(eval(repr(trans))))


if __name__ == '__main__':
    unittest.main()
