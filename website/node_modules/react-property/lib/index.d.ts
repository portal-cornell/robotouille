export const BOOLEAN: 3;
export const BOOLEANISH_STRING: 2;
export const NUMERIC: 5;
export const OVERLOADED_BOOLEAN: 4;
export const POSITIVE_NUMERIC: 6;
/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 *
 */
export const RESERVED: 0;
export const STRING: 1;
export function getPropertyInfo(name: any): any;
/**
 * Checks whether a property name is a custom attribute.
 *
 * @see https://github.com/facebook/react/blob/15-stable/src/renderers/dom/shared/HTMLDOMPropertyConfig.js#L23-L25
 *
 * @type {(attribute: string) => boolean}
 */
export const isCustomAttribute: (attribute: string) => boolean;
/**
 * @type {Record<string, string>}
 */
export const possibleStandardNames: Record<string, string>;
