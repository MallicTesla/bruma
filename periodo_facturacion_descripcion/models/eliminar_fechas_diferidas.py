# -*- coding: utf-8 -*-
"""
Módulo: Remover Fechas Diferidas
Descripción:
Este módulo garantiza que los campos "Fecha de inicio" (deferred_start_date)
y "Fecha de finalización" (deferred_end_date) del modelo `account.move.line`
no se asignen ni almacenen en ningún momento.
Siempre activo para borradores y cualquier creación o modificación de líneas de factura.
"""
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def default_get(self, fields_list):
        _logger.info('1- default_get: limpiando fechas diferidas por defecto')
        print('1- DEBUG: default_get account.move.line - limpiando deferred_start_date y deferred_end_date')
        res = super(AccountMoveLine, self).default_get(fields_list)
        if 'deferred_start_date' in res:
            res['deferred_start_date'] = False
        if 'deferred_end_date' in res:
            res['deferred_end_date'] = False
        return res

    @api.model
    def create(self, vals):
        _logger.info('2- create: limpiando fechas diferidas antes de crear línea')
        print('2- DEBUG: create account.move.line - forzando valores False en deferred_start_date y deferred_end_date')
        vals['deferred_start_date'] = False
        vals['deferred_end_date'] = False
        record = super(AccountMoveLine, self).create(vals)
        return record

    def write(self, vals):
        _logger.info('3- write: limpiando fechas diferidas antes de guardar cambios')
        print('3- DEBUG: write account.move.line - limpiando deferred_start_date y deferred_end_date si se intentan asignar')
        if 'deferred_start_date' in vals:
            vals['deferred_start_date'] = False
        if 'deferred_end_date' in vals:
            vals['deferred_end_date'] = False
        return super(AccountMoveLine, self).write(vals)


