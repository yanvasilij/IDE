#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief XSD file for MK201 module
@Author Vasilij
"""

CODEFILE_XSD = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <xsd:element name="%(codefile_name)s">
    <xsd:complexType>
      <xsd:sequence>
        %(includes_section)s
        <xsd:element name="variables">
          <xsd:complexType>
            <xsd:sequence>
              <xsd:element name="variable" minOccurs="0" maxOccurs="unbounded">
                <xsd:complexType>
                  <xsd:attribute name="name" type="xsd:string" use="required"/>
                  <xsd:attribute name="type" type="xsd:string" use="required"/>
                  <xsd:attribute name="class" use="optional">
                    <xsd:simpleType>
                      <xsd:restriction base="xsd:string">
                        <xsd:enumeration value="input"/>
                        <xsd:enumeration value="memory"/>
                        <xsd:enumeration value="output"/>
                      </xsd:restriction>
                    </xsd:simpleType>
                  </xsd:attribute>
                  <xsd:attribute name="initial" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="desc" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="onchange" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="opts" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="address" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="len" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="devid" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="txtype" type="xsd:string" use="optional" default=""/>
                  <xsd:attribute name="period" type="xsd:string" use="optional" default=""/>
                </xsd:complexType>
              </xsd:element>
            </xsd:sequence>
          </xsd:complexType>
        </xsd:element>
        %(sections)s
      </xsd:sequence>
    </xsd:complexType>
  </xsd:element>
  <xsd:complexType name="CodeText">
    <xsd:annotation>
      <xsd:documentation>Formatted text according to parts of XHTML 1.1</xsd:documentation>
    </xsd:annotation>
    <xsd:sequence>
      <xsd:any namespace="http://www.w3.org/1999/xhtml" processContents="lax"/>
    </xsd:sequence>
  </xsd:complexType>
</xsd:schema>"""
