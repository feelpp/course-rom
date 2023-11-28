//! -*- mode: c++; coding: utf-8; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4; show-trailing-whitespace: t  -*- vim:fenc=utf-8:ft=cpp:et:sw=4:ts=4:sts=4
//!
//! This file is part of the Feel++ library
//!
//! This library is free software; you can redistribute it and/or
//! modify it under the terms of the GNU Lesser General Public
//! License as published by the Free Software Foundation; either
//! version 2.1 of the License, or (at your option) any later version.
//!
//! This library is distributed in the hope that it will be useful,
//! but WITHOUT ANY WARRANTY; without even the implied warranty of
//! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//! Lesser General Public License for more details.
//!
//! You should have received a copy of the GNU Lesser General Public
//! License along with this library; if not, write to the Free Software
//! Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//!
//! @file
//! @brief Python bindings using pybind11 for the Laplacian example
//! @author Christophe Prud'homme <christophe.prudhomme@cemosis.fr>
//! @date 2023-10-31
//! @copyright 2023-2024 Feel++ Consortium
//! @copyright 2023 Université de Strasbourg
//!
#define PYBIND11_DETAILED_ERROR_MESSAGES
#include <feel/feelcore/environment.hpp>
#include <feel/feelcore/json.hpp>
#include <feel/feeldiscr/mesh.hpp>
#include <feel/feeldiscr/pch.hpp>
#include <feel/feelalg/vector.hpp>
#include <feel/feelalg/matrix.hpp>
#include <feel/feelpython/pybind11/eigen.h>
#include <feel/feelpython/pybind11/json.h>
#include <feel/feelpython/pybind11/pybind11.h>
#include <feel/feelpython/pybind11/stl.h>
#include <feel/feelpython/pybind11/stl_bind.h>

#include <feel/feelvf/vf.hpp>

#include <mpi4py/mpi4py.h>


namespace py = pybind11;

template<typename SpaceType>
void
bind_forms( py::module &m, std::string const& space_str )
{
    using namespace Feel;
#if 0
    py::enum_<Pattern>( m, "Pattern" )
        .value( "DEFAULT", Pattern::DEFAULT )
        .value( "EXTENDED", Pattern::EXTENDED )
        .value( "COUPLED", Pattern::COUPLED )
        .value( "PATTERN_SYMMETRIC", Pattern::PATTERN_SYMMETRIC )
        .value( "ZERO", Pattern::ZERO )
        .value( "HAS_NO_BLOCK_PATTERN", Pattern::HAS_NO_BLOCK_PATTERN )
        .value( "HDG", Pattern::HDG )
        .value( "NONE", Pattern::NONE )
        .export_values();
#endif
    
    using element_t = typename SpaceType::element_type;

    m.def("dot", [](element_t const& u, element_t const& v){ return u.dot(v); } );

    py::class_<form1_type<SpaceType>>( m, fmt::format( "form1_{}", space_str ).c_str() )
        .def( py::init<std::string,
                       std::shared_ptr<SpaceType> const&,
                       vector_ptrtype,
                       size_type,
                       bool,
                       bool,
                       double>(), "build a linear form", py::arg( "name" ), py::arg( "test" ), py::arg( "vector" ), py::arg( "rowstart" ) = 0, py::arg( "init" ) = true, py::arg( "do_threshold" ) = false, py::arg( "threshold" ) = 0.0 )
        .def("zero", [](form1_type<SpaceType> &a) {
                // Define the set to zero operation
                a.zero();
            }, "Set the form to zero")
        .def("scale", [](form1_type<SpaceType> &a, double factor) {
                // Define the scaling operation
                a.scale(factor);
            }, "Scale the form by a factor", py::arg("factor"))
        .def("__assign__", [](form1_type<SpaceType> &a, const form1_type<SpaceType> &b) {
                // Define assignment operation
                a = b;
                return a;
            }, "Assign one form to another", py::return_value_policy::reference_internal)
        .def("__iadd__", [](form1_type<SpaceType> &a, const form1_type<SpaceType> &b) {
                // Define how the in-place addition should be performed
                a += b;
                return a;
            }, "In-place add two forms", py::return_value_policy::reference_internal)
        .def("__add__", [](const form1_type<SpaceType> &a, const form1_type<SpaceType> &b) {
                // Define how the addition should be performed
                return a + b;
            }, "Add two forms")
        .def("__neg__", [](const form1_type<SpaceType> &a) {
                form1_type<SpaceType> b {a};
                b.scale(-1); 
                return b;
            }, "Negate the form")
        .def("__rmul__", [](const form1_type<SpaceType> &a, double alpha) {
                auto l = a;
                l.scale(alpha);
                return l; 
            }, "Multiply form with a scalar from right", py::is_operator())
        .def("__mul__", [](const form1_type<SpaceType> &a, double alpha) {
            auto l = a;
            l.scale(alpha);
            return l; 
            }, "Multiply form with a scalar from left", py::is_operator())
        .def( "__call__", []( form1_type<SpaceType> const& f, element_t const b )
          { return f( b ); } );

    m.def(
        "form1", []( std::shared_ptr<SpaceType> const& test, vector_ptrtype vector, std::string const& name, size_type rowstart, bool init, bool do_threshold, double threshold )
        { 
            if ( !vector )
                vector = backend()->newVector( _test=test );
            return form1( _name = name, _test = test, _vector = vector, _rowstart = rowstart, _init = init, _do_threshold = do_threshold, _threshold = threshold ); 
        },
        "build a linear form", py::arg( "test" ), py::arg( "vector" ) = py::none(), py::arg( "name" ) = "linearform.f", py::arg( "rowstart" ) = 0, py::arg( "init" ) = true, py::arg( "do_threshold" ) = false, py::arg( "threshold" ) = 0.0 );

    py::class_<form2_type<SpaceType, SpaceType>>( m, fmt::format( "form2_{}", space_str ).c_str() )
        .def( py::init<std::string,
                       std::shared_ptr<SpaceType> const&,
                       std::shared_ptr<SpaceType> const&,
                       d_sparse_matrix_ptrtype&,
                       size_type,
                       size_type,
                       bool,
                       bool,
                       double,
                       size_type>(),
              "build a linear form", py::arg( "name" ), py::arg( "test" ), py::arg( "trial" ), py::arg( "matrix" ) = py::none(), py::arg( "rowstart" ) = 0, py::arg( "colstart" ) = 0, py::arg( "init" ) = true, py::arg( "do_threshold" ) = false, py::arg( "threshold" ) = 0.0, py::arg( "hints" ) = (int)Pattern::COUPLED )
        .def(
            "zero", []( form2_type<SpaceType, SpaceType>& a )
            {
                // Define the set to zero operation
                a.zero(); },
            "Set the form to zero" )
        //.def("scale", [](form2_type<SpaceType,SpaceType> &a, double factor) {
        //        // Define the scaling operation
        //        a.scale(factor);
        //    }, "Scale the form by a factor", py::arg("factor"))
        .def(
            "__assign__", []( form2_type<SpaceType, SpaceType>& a, const form2_type<SpaceType, SpaceType>& b )
            {
                // Define assignment operation
                a = b;
                return a; },
            "Assign one form to another", py::return_value_policy::reference_internal )
        .def(
            "__iadd__", []( form2_type<SpaceType, SpaceType>& a, form2_type<SpaceType, SpaceType>& b )
            {
                // Define how the in-place addition should be performed
                dynamic_cast<BilinearFormBase<>&>(a) += dynamic_cast<BilinearFormBase<>&>(b);
                return a; },
            "In-place add two forms", py::return_value_policy::reference_internal )
        .def(
            "__add__", []( const form2_type<SpaceType, SpaceType>& a, form2_type<SpaceType, SpaceType>& b )
            {
                auto l = form2( _test = a.testSpace(), _trial = a.trialSpace() );
                l.close();
                l=a;
                dynamic_cast<BilinearFormBase<>&>( l ) += dynamic_cast<BilinearFormBase<>&>( b );
                return l; },
            "Add two forms" )
        .def(
            "__neg__", []( form2_type<SpaceType, SpaceType>& a )
            { 
                auto l = form2( _test = a.testSpace(), _trial = a.trialSpace() );
                l.close();
                dynamic_cast<BilinearFormBase<>&>( l ).add( -1, dynamic_cast<BilinearFormBase<>&>(a) );
                return l; },
            "Negate the form" )
        .def(
            "__rmul__", []( form2_type<SpaceType, SpaceType>& a, double alpha )
            {
                            LOG(INFO) << fmt::format("rmul with {}",alpha) << std::endl;
                            auto l = form2(_test=a.testSpace(),_trial=a.trialSpace());
                            l.close();
                            dynamic_cast<BilinearFormBase<>&>(l).add(alpha,dynamic_cast<BilinearFormBase<>&>(a));
                            return l; },
            "Multiply form with a scalar from right" )
        .def(
            "__mul__", []( form2_type<SpaceType, SpaceType>& a, double alpha )
            {
                LOG(INFO) << fmt::format("mul with {}",alpha) << std::endl;
                auto l = form2( _test = a.testSpace(), _trial = a.trialSpace() );
                l.close();
                dynamic_cast<BilinearFormBase<>&>(l).add(alpha,dynamic_cast<BilinearFormBase<>&>(a));
                return l; 
            },
            "Multiply form with a scalar from left" )
        .def( "__call__", []( form2_type<SpaceType, SpaceType> const& a, element_t const& u, element_t const& v )
              { return a( u, v ); } )
        .def(
            "solve", []( form2_type<SpaceType, SpaceType>& a, element_t& u, form1_type<SpaceType> const& f, bool rebuild )
            { a.solve( _solution = u, _rhs = f, _rebuild=rebuild ); },
            "solve the linear system find u s.t. a(u,v)=f(v) for all v", py::arg( "solution" ), py::arg( "rhs" ), py::arg("rebuild") = true );

    m.def(
        "form2", []( std::shared_ptr<SpaceType> const& test, std::shared_ptr<SpaceType> const& trial, d_sparse_matrix_ptrtype& matrix, std::string const& name, size_type rowstart, size_type colstart, bool init, bool do_threshold, double threshold )
        { return form2( _name = name, _test = test, _trial = trial, _matrix = matrix, _rowstart = rowstart, _colstart = colstart, _init = init, _do_threshold = do_threshold, _threshold = threshold ); },
        "build a bilinear form", py::arg( "test" ), py::arg( "trial" ), py::arg( "matrix" ) = py::none(), py::arg( "name" ) = "bilinearform.a", py::arg( "rowstart" ) = 0, py::arg( "colstart" ) = 0, py::arg( "init" ) = true, py::arg( "do_threshold" ) = false, py::arg( "threshold" ) = 0.0 );
}
PYBIND11_MODULE(_forms, m )
{
    if (import_mpi4py()<0) return ;
    m.doc() = fmt::format("Python bindings for linear and bilinear forms" );
    using namespace Feel;
    bind_forms<Pch_type<Mesh<Simplex<2,1>>,1>>(m,"Pch_2DP1");
    bind_forms<Pch_type<Mesh<Simplex<2,1>>,2>>(m,"Pch_2DP2");

}
