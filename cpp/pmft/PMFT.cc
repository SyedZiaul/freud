// Copyright (c) 2010-2018 The Regents of the University of Michigan
// This file is part of the freud project, released under the BSD 3-Clause License.

#include "PMFT.h"
#include "ScopedGILRelease.h"

#include <stdexcept>
#ifdef __SSE2__
#include <emmintrin.h>
#endif

using namespace std;
using namespace tbb;

/*! \internal
    \file PMFT.cc
    \brief Contains code for PMFT class
*/

namespace freud { namespace pmft {

/*! All PMFT classes have the same deletion logic
 */
PMFT::~PMFT()
    {
    for (tbb::enumerable_thread_specific<unsigned int *>::iterator i = m_local_bin_counts.begin(); i != m_local_bin_counts.end(); ++i)
        {
        delete[] (*i);
        }
    }

//! Get a reference to the PCF array
std::shared_ptr<unsigned int> PMFT::getBinCounts()
    {
    if (m_reduce == true)
        {
        reducePCF();
        }
    m_reduce = false;
    return m_bin_counts;
    }

//! Get a reference to the PCF array
std::shared_ptr<float> PMFT::getPCF()
    {
    if (m_reduce == true)
        {
        reducePCF();
        }
    m_reduce = false;
    return m_pcf_array;
    }

}; }; // end namespace freud::pmft
